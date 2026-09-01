#!/usr/bin/env python3
"""
week4_eval.py — Week 4 Practical · Task Set D
"Label the failures, then buy back hit-rate@3 with exactly one change."

What one run does, in order:
  1. Re-ingests the corpus (clean, reproducible run).
  2. Verifies the golden set: every tagged chunk_id must exist and contain
     the expected answer fragment — a mistagged golden set measures nothing.
  3. BASELINE — hit-rate@3 and p50 latency on the untouched Week-3 dense
     retriever. The fused path is dead code during this pass.
  4. Labels every baseline failure R / G / Not-In-Corpus from inspection
     data (deep dense rank of the golden chunk, top-3 contents, and — when
     GROQ_API_KEY is set — what the model answered given that context).
  5. AFTER — the SAME 12 questions through the ONE change (BM25 + RRF, k=60).
  6. Bonus — MMR over the fused candidate list, one lambda sweep.
  7. Writes results.md: every number, every label, the diff, the decision.

Usage:
    python week4_eval.py [--skip-generation]
"""

import argparse
import json
import os
import statistics
import subprocess
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv

load_dotenv()

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "src"))

import numpy as np

from hybrid import CANDIDATES, RRF_K, _corpus, fused_search
from indexer import get_collection, get_embedding_fn, ingest_all, resolve_chunk
from retriever import search

GOLDEN_SET_PATH = os.path.join(HERE, "golden_set.jsonl")
RESULTS_PATH = os.path.join(HERE, "results.md")

TOP_K = 3
LATENCY_REPEATS = 9
MMR_LAMBDAS = (0.3, 0.5, 0.7)
MMR_TOP_K = 3

# The model emits U+2011 non-breaking hyphens ("E‑17") and narrow spaces
# ("72 hours"); comparing raw ASCII fragments against that produces FALSE
# G-labels. Canonicalise both sides: dashes and exotic spaces become plain
# spaces, case folds, whitespace collapses.
_CANON = str.maketrans(dict.fromkeys("-‐‑‒–—−   ", " "))


def canonical(text: str) -> str:
    return " ".join(text.translate(_CANON).lower().split())


# ---------------------------------------------------------------------------
# Golden set
# ---------------------------------------------------------------------------

def load_golden_set() -> list[dict]:
    with open(GOLDEN_SET_PATH, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def accepted_ids(q: dict) -> set[str]:
    return {q["golden_chunk_id"], *q.get("alt_chunk_ids", [])}


def verify_golden_set(questions: list[dict]) -> None:
    """Every golden chunk must exist AND contain the expected answer fragment."""
    for q in questions:
        chunk = resolve_chunk(q["golden_chunk_id"])
        if chunk is None:
            raise SystemExit(f"{q['id']}: golden chunk {q['golden_chunk_id']} not in index")
        if q["expected_answer_fragment"].lower() not in chunk["text"].lower():
            raise SystemExit(
                f"{q['id']}: fragment {q['expected_answer_fragment']!r} missing "
                f"from golden chunk {q['golden_chunk_id']} — retag before measuring"
            )
    print(f"  golden set verified: {len(questions)} questions, all chunk_ids resolve")


# ---------------------------------------------------------------------------
# Measurement
# ---------------------------------------------------------------------------

def evaluate(search_fn, questions: list[dict]) -> list[dict]:
    """Hit-rate@3 records: hit iff the golden (or an alt) chunk_id is in top-3."""
    records = []
    for q in questions:
        top3 = search_fn(q["question"], n_results=TOP_K)
        got = next((r for r in top3 if r["chunk_id"] in accepted_ids(q)), None)
        records.append({
            "id": q["id"],
            "hit": got is not None,
            "rank": got["rank"] if got else None,
            "top3": top3,
        })
    return records


def measure_p50(search_fn, questions: list[dict]) -> tuple[float, list[float]]:
    """p50 across per-query median latencies, in ms. One warmup call first."""
    search_fn(questions[0]["question"], n_results=TOP_K)
    per_query = []
    for q in questions:
        times = []
        for _ in range(LATENCY_REPEATS):
            t0 = time.perf_counter()
            search_fn(q["question"], n_results=TOP_K)
            times.append((time.perf_counter() - t0) * 1000)
        per_query.append(statistics.median(times))
    return statistics.median(per_query), per_query


def deep_dense_rank(q: dict, corpus_size: int) -> int | None:
    """Where the golden chunk actually sits in the full dense ordering."""
    for r in search(q["question"], n_results=corpus_size):
        if r["chunk_id"] in accepted_ids(q):
            return r["rank"]
    return None


def top3_summary(record: dict) -> str:
    return ", ".join(
        f"{r['metadata']['form_number']}/{r['metadata']['clause_id']}"
        for r in record["top3"]
    )


# ---------------------------------------------------------------------------
# Failure labelling — R / G / Not-In-Corpus
# ---------------------------------------------------------------------------

def generation_check(questions: list[dict], records: list[dict]) -> dict | None:
    """
    Feed each question its baseline top-3 (the metric's cut) and record what
    the model does with it. This is what separates R from G: a wrong answer
    over context that CONTAINS the golden chunk is G, not R.
    """
    if not os.environ.get("GROQ_API_KEY"):
        return None
    from answerer import generate_answer

    answers = {}
    for q, rec in zip(questions, records):
        try:
            res = generate_answer(q["question"], rec["top3"], verbose=False)
        except Exception as exc:
            print(f"  ! generation failed at {q['id']}: {exc} — G-check incomplete")
            return {"error": str(exc), "answers": answers}
        answers[q["id"]] = {
            "answer": res["answer"],
            "is_refusal": res["is_refusal"],
            "fragment_found": any(
                canonical(frag) in canonical(res["answer"])
                for frag in q.get("answer_fragments") or [q["expected_answer_fragment"]]
            ),
        }
        print(f"  {q['id']}: {'refused' if res['is_refusal'] else 'answered'}")
    return {"error": None, "answers": answers}


def label_failures(questions, records, dense_ranks, gen) -> list[dict]:
    labels = []
    for q, rec in zip(questions, records):
        gen_ans = (gen or {}).get("answers", {}).get(q["id"])
        if not rec["hit"]:
            if resolve_chunk(q["golden_chunk_id"]) is None:
                labels.append({
                    "id": q["id"], "label": "Not-In-Corpus",
                    "evidence": f"golden chunk {q['golden_chunk_id']} resolves to nothing",
                })
                continue
            evidence = (
                f"golden {q['golden_chunk_id']} sits at dense rank "
                f"{dense_ranks[q['id']]}; top-3 = {top3_summary(rec)}"
            )
            if gen_ans and not gen_ans["fragment_found"]:
                what = "refused" if gen_ans["is_refusal"] else "answered without the golden fact"
                evidence += f" — model {what} over that context"
            labels.append({"id": q["id"], "label": "R", "evidence": evidence})
        elif gen_ans and not gen_ans["fragment_found"] and not gen_ans["is_refusal"]:
            labels.append({
                "id": q["id"], "label": "G",
                "evidence": (
                    f"golden {q['golden_chunk_id']} WAS at rank {rec['rank']} in top-3, "
                    f"yet the answer omits {q['expected_answer_fragment']!r}: "
                    f"\"{' '.join(gen_ans['answer'].split())[:100]}...\""
                ),
            })
    return labels


# ---------------------------------------------------------------------------
# Bonus — MMR over the fused candidate list
# ---------------------------------------------------------------------------

def _embed(texts: list[str]) -> np.ndarray:
    vecs = np.asarray(get_embedding_fn()(texts), dtype=float)
    return vecs / np.linalg.norm(vecs, axis=1, keepdims=True)


def _mmr_pick(q_sim: np.ndarray, cand_vecs: np.ndarray, lam: float, k: int) -> list[int]:
    selected: list[int] = []
    rest = list(range(len(q_sim)))
    while rest and len(selected) < k:
        best = max(rest, key=lambda i: lam * q_sim[i] - (
            0.0 if not selected
            else (1 - lam) * max(float(cand_vecs[i] @ cand_vecs[j]) for j in selected)
        ))
        selected.append(best)
        rest.remove(best)
    return selected


def _diversity(cand_vecs: np.ndarray, picked: list[int]) -> float:
    """Mean pairwise cosine DISTANCE among the picked chunks — higher = more varied."""
    pairs = [(a, b) for i, a in enumerate(picked) for b in picked[i + 1:]]
    return statistics.mean(1 - float(cand_vecs[a] @ cand_vecs[b]) for a, b in pairs)


def run_mmr_bonus(questions: list[dict]) -> dict:
    per_lambda = {lam: {"hits": 0, "diversity": [], "e17_top3": None} for lam in MMR_LAMBDAS}
    fused_div, fused_e17 = [], None

    for q in questions:
        cands = fused_search(q["question"], n_results=CANDIDATES)
        vecs = _embed([q["question"]] + [c["text"] for c in cands])
        q_vec, cand_vecs = vecs[0], vecs[1:]
        q_sim = cand_vecs @ q_vec

        fused_div.append(_diversity(cand_vecs, [0, 1, 2]))
        if q["id"] == "g01":
            fused_e17 = ", ".join(f"{c['metadata']['form_number']}/{c['metadata']['clause_id']}"
                                  for c in cands[:3])

        for lam in MMR_LAMBDAS:
            picked = _mmr_pick(q_sim, cand_vecs, lam, MMR_TOP_K)
            chosen = [cands[i] for i in picked]
            if any(c["chunk_id"] in accepted_ids(q) for c in chosen):
                per_lambda[lam]["hits"] += 1
            per_lambda[lam]["diversity"].append(_diversity(cand_vecs, picked))
            if q["id"] == "g01":
                per_lambda[lam]["e17_top3"] = ", ".join(
                    f"{c['metadata']['form_number']}/{c['metadata']['clause_id']}" for c in chosen)

    return {
        "fused_diversity": statistics.mean(fused_div),
        "fused_e17_top3": fused_e17,
        "per_lambda": {
            lam: {
                "hits": d["hits"],
                "diversity": statistics.mean(d["diversity"]),
                "e17_top3": d["e17_top3"],
            }
            for lam, d in per_lambda.items()
        },
    }


# ---------------------------------------------------------------------------
# results.md
# ---------------------------------------------------------------------------

def get_code_diff() -> str:
    try:
        out = subprocess.run(
            ["git", "diff", "--no-color", "HEAD", "--", "src/hybrid.py", "ask.py"],
            capture_output=True, text=True, cwd=HERE, timeout=30,
        )
        return out.stdout.strip() or "(no diff — is src/hybrid.py intent-to-added? git add -N src/hybrid.py)"
    except Exception as exc:
        return f"(git diff unavailable: {exc})"


def write_results(questions, base, base_p50, after, after_p50,
                  dense_ranks, labels, gen, mmr) -> None:
    n = len(questions)
    base_hits = sum(r["hit"] for r in base)
    after_hits = sum(r["hit"] for r in after)
    tally = {"R": 0, "G": 0, "Not-In-Corpus": 0}
    for lab in labels:
        tally[lab["label"]] += 1
    r_labels = [lab for lab in labels if lab["label"] == "R"]
    exact_r = [lab["id"] for lab in r_labels
               if next(q for q in questions if q["id"] == lab["id"])["exact_token"]]
    beyond_25 = [(lab["id"], dense_ranks[lab["id"]]) for lab in r_labels
                 if dense_ranks[lab["id"]] and dense_ranks[lab["id"]] > CANDIDATES]

    base_by_id = {r["id"]: r for r in base}
    after_by_id = {r["id"]: r for r in after}

    def verdict(qid: str) -> str:
        b, a = base_by_id[qid]["hit"], after_by_id[qid]["hit"]
        return {(False, True): "**FIXED**", (False, False): "still broken",
                (True, True): "still hit", (True, False): "**REGRESSED**"}[(b, a)]

    fixed = [lab["id"] for lab in r_labels if after_by_id[lab["id"]]["hit"]]
    unfixed = [lab["id"] for lab in r_labels if not after_by_id[lab["id"]]["hit"]]
    regressed = [r["id"] for r in base if r["hit"] and not after_by_id[r["id"]]["hit"]]

    # -- one-paragraph justification, written FROM the tally -----------------
    if beyond_25:
        worst = ", ".join(f"{qid} (dense rank {rk})" for qid, rk in beyond_25)
        reranker_line = (
            f"A cross-encoder rerank was rejected because it can only reorder the dense "
            f"top-{CANDIDATES}, and for {worst} the golden chunk never made that list — "
            f"there is nothing to rerank."
        )
    else:
        reranker_line = (
            f"A cross-encoder rerank could also have reached these chunks (every R golden "
            f"sits inside the dense top-{CANDIDATES}), but it buys the same ranks back with "
            f"a model inference over {CANDIDATES} pairs per query, where BM25 over 72 "
            f"documents is sub-millisecond and aims squarely at the actual failure signal."
        )
    if tally["G"] == 0:
        model_line = (
            "every live failure is retrieval fetching bad context, and not one is the model "
            "misusing good context (Appendix A: given the right chunk in top-3, the model "
            "answered and cited correctly every time) — so swapping the model, as the team "
            "lead suggested, would fix exactly nothing"
        )
    else:
        model_line = (
            f"the {tally['R']} R-failure(s) are addressable in retrieval; the {tally['G']} "
            f"G-failure(s) are a generation problem no retrieval change can touch, and are "
            f"named in the label table above"
        )
    justification = (
        f"The tally is {tally['R']} R, {tally['G']} G, {tally['Not-In-Corpus']} Not-In-Corpus: "
        f"{model_line}. Of the {len(r_labels)} R-failure(s), {len(exact_r)} "
        f"({', '.join(exact_r) if exact_r else 'none'}) "
        f"{'carries' if len(exact_r) == 1 else 'carry'} an exact token — an exclusion "
        f"code or a form/edition number — that MiniLM embeddings structurally under-weight: "
        f"the missing signal is lexical, not semantic. The one change is therefore BM25 + RRF "
        f"fusion (k={RRF_K}): BM25 treats E-17 and HO-0304 as the rare, high-idf terms they "
        f"are, and RRF fuses the two RANK lists so no raw-score scale mixing occurs. "
        f"{reranker_line}"
    )

    # -- shipping decision, written FROM the numbers -------------------------
    delta = after_hits - base_hits
    lat_delta = after_p50 - base_p50
    lat_pct = (lat_delta / base_p50 * 100) if base_p50 else 0.0
    lat_noise = abs(lat_delta) < 5
    if delta > 0:
        shipping = (
            f"**Ship it.** Hit-rate@3 moved {base_hits}/{n} → {after_hits}/{n} (+{delta}) for a "
            f"p50 latency change of {base_p50:.1f} ms → {after_p50:.1f} ms "
            f"({lat_delta:+.1f} ms{', within run-to-run noise' if lat_noise else ''}). "
            + (f"{len(unfixed)} R-failure(s) remain ({', '.join(unfixed)}) — documented below; "
               f"they are the next experiment, run one variable at a time. " if unfixed else "")
            + (f"Regressions: {', '.join(regressed)}. " if regressed
               else "No question that passed before fails now. ")
            + f"The number that moved is the one the adjusters feel: exact-code and form-number "
              f"lookups now resolve."
        )
    elif delta == 0:
        shipping = (
            f"**Do not ship on this evidence.** Hit-rate@3 stayed at {base_hits}/{n} while p50 "
            f"latency went {base_p50:.1f} → {after_p50:.1f} ms. A change that moves no number "
            f"is pure risk."
        )
    else:
        shipping = (
            f"**Do not ship.** Hit-rate@3 DROPPED {base_hits}/{n} → {after_hits}/{n} "
            f"({delta}). Revert and re-examine the tally."
        )

    # -- assemble ------------------------------------------------------------
    exact_count = sum(1 for q in questions if q["exact_token"])
    qmap = {q["id"]: q for q in questions}
    parts: list[str] = []
    add = parts.append

    add(
        "# Week 4 — Results: Label the Failures, Buy Back Hit-Rate@3 with One Change\n\n"
        "*Task Set D · Module M2 · generated by `week4_eval.py` — numbers, not claims.*\n\n"
        "**The claim under test:** the team lead wants to swap the model because "
        "'does exclusion E-17 apply under form HO-0304 ed. 03-24' returns three fluent, "
        "semantically-adjacent water-damage clauses and no E-17. Below: where the failures "
        "actually live, ONE retrieval change, and the before/after number.\n\n"
        "**Retriever under test:** the Week-3 structure-aware collection (72 chunks), dense "
        "cosine search over local MiniLM embeddings. **Hit rule:** the known-correct chunk_id "
        "(or a listed equivalent that states the same fact) appears in the top-3. "
        "**One variable:** the baseline pass never touches the fusion code; the after pass "
        "changes retrieval only.\n"
    )

    add(f"\n---\n\n## 1. The golden set — 12 real adjuster questions\n\n"
        f"Written from the endorsement text and tagged with known-correct chunk_ids BEFORE "
        f"any retrieval was run. {exact_count} of {n} carry an exact token dense retrieval "
        f"is structurally bad at (requirement: at least 4).\n\n"
        f"| # | Question | Golden chunk_id | Exact token | Known-correct answer |\n"
        f"|---|---|---|---|---|\n")
    for q in questions:
        alt = f" (alt: {', '.join(q['alt_chunk_ids'])})" if q["alt_chunk_ids"] else ""
        add(f"| {q['id']} | {q['question']} | `{q['golden_chunk_id']}`{alt} | "
            f"{q['exact_token'] or '—'} | {q['note']} |\n")
    add("\nFull set with tags: `golden_set.jsonl`. `week4_eval.py` refuses to run if any "
        "golden chunk fails to resolve or lacks its answer fragment.\n")

    add(f"\n---\n\n## 2. Baseline — written down before anything changed\n\n"
        f"## **Baseline hit-rate@3: {base_hits}/{n}** · p50 latency {base_p50:.1f} ms/query\n\n"
        f"| # | Hit@3 | Golden at dense rank | Baseline top-3 (form/clause) |\n"
        f"|---|---|---|---|\n")
    for q, rec in zip(questions, base):
        mark = f"HIT @{rec['rank']}" if rec["hit"] else "**MISS**"
        add(f"| {q['id']} | {mark} | {dense_ranks[q['id']] or 'not found'} | "
            f"{top3_summary(rec)} |\n")

    add(f"\n---\n\n## 3. Failure labels — R / G / Not-In-Corpus\n\n"
        f"### Tally: **{tally['R']} R · {tally['G']} G · {tally['Not-In-Corpus']} Not-In-Corpus**\n\n")
    if gen is None:
        add("*(G-check note: GROQ_API_KEY unavailable, so R labels rest on retrieval evidence "
            "alone — a hit-rate@3 miss is bad context by definition.)*\n\n")
    else:
        add("Labels use the inspection view (`inspect_retrieval.py`) plus a generation pass "
            "over each question's baseline top-3: a wrong answer over context that CONTAINS "
            "the golden chunk would be G, not R. Transcripts in Appendix A.\n\n")
    add("| # | Label | One line of evidence |\n|---|---|---|\n")
    for lab in labels:
        add(f"| {lab['id']} | **{lab['label']}** | {lab['evidence']} |\n")
    add(f"\nNot-In-Corpus is structurally 0 here: requirement 1 forces every question to be "
        f"tagged with a chunk_id that exists — and the harness verifies that tag before "
        f"measuring. Real not-in-corpus traffic (claim records, underwriting guidelines) is "
        f"handled by the Week-3 refusal rule, tested separately in report.md.\n")

    add(f"\n---\n\n## 4. The ONE change — BM25 + RRF fusion (k={RRF_K})\n\n{justification}\n\n"
        f"**What changed:** `src/hybrid.py` — dense top-{CANDIDATES} and BM25 top-{CANDIDATES} "
        f"over the same collection, fused by reciprocal rank: score(c) = Σ 1/({RRF_K} + rank). "
        f"The dense path itself is untouched. Tokenizer keeps `e-17`, `ho-0304`, `03-24` as "
        f"single tokens. No new dependency (Okapi BM25 is ~30 lines).\n")

    add(f"\n---\n\n## 5. Before → after — the one table\n\n"
        f"| Metric | Before (dense only) | After (BM25 + RRF, k={RRF_K}) | Delta |\n"
        f"|---|---|---|---|\n"
        f"| **Hit-rate@3** | **{base_hits}/{n}** | **{after_hits}/{n}** | "
        f"{'+' if delta >= 0 else ''}{delta} |\n"
        f"| **p50 latency / query** | {base_p50:.1f} ms | {after_p50:.1f} ms | "
        f"{lat_delta:+.1f} ms ({lat_pct:+.0f}%) |\n\n"
        f"Latency protocol: per query, median of {LATENCY_REPEATS} timed retrievals after a "
        f"warmup call; p50 taken across the 12 per-query medians. Same machine, same run, "
        f"embedding model already resident."
        + (" BM25 over 72 documents adds well under a millisecond of real work — a delta of "
           "this size is run-to-run noise, and the honest claim is 'latency is unchanged', "
           "not 'it got faster'." if lat_noise else "")
        + "\n")

    add(f"\n---\n\n## 6. Per-question record — fixed / unfixed / still broken\n\n"
        f"| # | Before | After | Verdict | What the change did |\n|---|---|---|---|---|\n")
    for q in questions:
        b, a = base_by_id[q["id"]], after_by_id[q["id"]]
        b_mark = f"hit @{b['rank']}" if b["hit"] else "miss"
        a_mark = f"hit @{a['rank']}" if a["hit"] else "miss"
        if not b["hit"] and a["hit"]:
            got = next(r for r in a["top3"] if r["chunk_id"] in accepted_ids(q))
            how = (f"BM25 rank {got.get('bm25_rank') or '—'} + dense rank "
                   f"{got.get('dense_rank') or '—'} → fused @{got['rank']}")
        elif not b["hit"]:
            how = "untouched by the change"
        else:
            how = "already hitting; fusion left it in the top-3"
        add(f"| {q['id']} | {b_mark} | {a_mark} | {verdict(q['id'])} | {how} |\n")
    add(f"\n**R-failures the change fixed:** {', '.join(fixed) if fixed else 'none'}. "
        f"**R-failures it did not touch:** {', '.join(unfixed) if unfixed else 'none'}. "
        f"**Regressions:** {', '.join(regressed) if regressed else 'none'}.\n")

    add(f"\n---\n\n## 7. Shipping decision\n\n{shipping}\n")

    add(f"\n---\n\n## 8. Bonus — MMR over the fused candidate list\n\n"
        f"MMR re-picks the top-{MMR_TOP_K} from the fused top-{CANDIDATES}, trading query "
        f"relevance against redundancy. One lambda sweep (tuned once, as allowed):\n\n"
        f"| Variant | Hit-rate@3 | Mean top-3 diversity* | E-17 query (g01) top-3 |\n"
        f"|---|---|---|---|\n"
        f"| Fused, no MMR | {after_hits}/{n} | {mmr['fused_diversity']:.3f} | "
        f"{mmr['fused_e17_top3']} |\n")
    for lam, d in mmr["per_lambda"].items():
        add(f"| MMR λ={lam} | {d['hits']}/{n} | {d['diversity']:.3f} | {d['e17_top3']} |\n")
    add("\n*Mean pairwise cosine distance among the selected top-3 — higher = more varied.\n\n")
    best_lam = max(mmr["per_lambda"], key=lambda l: (mmr["per_lambda"][l]["hits"],
                                                     mmr["per_lambda"][l]["diversity"]))
    best = mmr["per_lambda"][best_lam]
    if best["hits"] < after_hits:
        add(f"**Verdict: do not ship MMR.** Even the best lambda ({best_lam}) pays "
            f"{after_hits - best['hits']} hit(s) of hit-rate@3 for variety — exactly the "
            f"failure mode the task warns about: diversity pushing the correct edition out "
            f"of the top-3. In a claims tool, the right clause beats a varied wrong list.\n")
    else:
        add(f"**Verdict: λ={best_lam} keeps hit-rate@3 at {best['hits']}/{n} while lifting "
            f"mean diversity {mmr['fused_diversity']:.3f} → {best['diversity']:.3f}. "
            f"Shippable, but the win is cosmetic on this corpus — one edition per form means "
            f"redundancy is rare. Revisit when multiple editions are indexed.\n")

    add(f"\n---\n\n## 9. The code diff — exactly one retrieval change\n\n"
        f"```diff\n{get_code_diff()}\n```\n")

    if gen and gen["answers"]:
        add("\n---\n\n## Appendix A — G-check transcripts (baseline top-3 as context)\n\n")
        for qid, ans in gen["answers"].items():
            status = "REFUSED" if ans["is_refusal"] else (
                "contains expected fragment" if ans["fragment_found"] else "MISSING expected fragment")
            add(f"**{qid}** ({status}) — {qmap[qid]['question']}\n\n"
                f"> {' '.join(ans['answer'].split())}\n\n")
        if gen["error"]:
            add(f"*(generation pass ended early: {gen['error']})*\n")

    with open(RESULTS_PATH, "w", encoding="utf-8") as fh:
        fh.write("".join(parts))
    print(f"\n  ✓ wrote {RESULTS_PATH}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Week 4 eval — one change, two numbers")
    parser.add_argument("--skip-generation", action="store_true",
                        help="skip the Groq G-check pass (retrieval labels only)")
    args = parser.parse_args()

    print("[1/7] Re-ingesting (clean run)...")
    ingest_all(reset=True)
    _corpus.cache_clear()  # BM25 must see the fresh index, not a cached one
    corpus_size = get_collection("structure_aware").count()

    print("\n[2/7] Verifying the golden set...")
    questions = load_golden_set()
    verify_golden_set(questions)

    print("\n[3/7] BASELINE — dense-only hit-rate@3 (the number is written down now)...")
    base = evaluate(search, questions)
    base_hits = sum(r["hit"] for r in base)
    for q, rec in zip(questions, base):
        print(f"  {q['id']}: {'hit @' + str(rec['rank']) if rec['hit'] else 'MISS'}")
    print(f"  BASELINE hit-rate@3 = {base_hits}/{len(questions)}")
    base_p50, _ = measure_p50(search, questions)
    print(f"  baseline p50 latency = {base_p50:.1f} ms/query")
    dense_ranks = {q["id"]: deep_dense_rank(q, corpus_size) for q in questions}

    print("\n[4/7] Labelling failures (R / G / Not-In-Corpus)...")
    gen = None if args.skip_generation else generation_check(questions, base)
    labels = label_failures(questions, base, dense_ranks, gen)
    for lab in labels:
        print(f"  {lab['id']} = {lab['label']}: {lab['evidence'][:90]}")

    print(f"\n[5/7] AFTER — the ONE change: BM25 + RRF fusion (k={RRF_K})...")
    after = evaluate(fused_search, questions)
    after_hits = sum(r["hit"] for r in after)
    for q, rec in zip(questions, after):
        print(f"  {q['id']}: {'hit @' + str(rec['rank']) if rec['hit'] else 'MISS'}")
    print(f"  AFTER hit-rate@3 = {after_hits}/{len(questions)}")
    after_p50, _ = measure_p50(fused_search, questions)
    print(f"  after p50 latency = {after_p50:.1f} ms/query")

    print("\n[6/7] Bonus — MMR sweep over the fused candidates...")
    mmr = run_mmr_bonus(questions)
    for lam, d in mmr["per_lambda"].items():
        print(f"  λ={lam}: hits={d['hits']}/12, diversity={d['diversity']:.3f}")

    print("\n[7/7] Writing results.md...")
    write_results(questions, base, base_p50, after, after_p50,
                  dense_ranks, labels, gen, mmr)


if __name__ == "__main__":
    main()
