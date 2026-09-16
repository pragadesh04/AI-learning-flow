#!/usr/bin/env python3
"""
week6_eval.py — Week 6: validate the claim-summary judge before trusting it.

One command runs everything and prints pass rate by failure mode:

    python week6_eval.py                    # generate missing outputs, 5 assertions,
                                            # judge (latest judge_vN.txt), tables

The blind protocol, in the order it has to happen:

    python week6_eval.py generate           # 25 summaries + 4 replayed traces, frozen
    python week6_eval.py label              # hand-label 25 summaries (interactive)
    python week6_eval.py packet             # ...or: a reading packet + labels template
    git add evals/labels_25.json && git commit    # <- the ordering evidence
    python week6_eval.py judge --version v1 # refuses to run before that commit
    python week6_eval.py agreement --version v1
    # write evals/prediction.txt, commit it, write judge_v2.txt from v1's disagreements
    python week6_eval.py judge --version v2
    python week6_eval.py agreement --version v2
"""

import argparse
import json
import os
import random
import re
import sys
import time
from collections import defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv

load_dotenv()

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "src"))

from assertions import ASSERTIONS, run_assertions
from judge import (EVAL_DIR, LABELS_PATH, BlindProtocolError, criterion_text,
                   judge_one, judge_path, labels_commit, policy_wording, template_sha)

CASES_PATH = os.path.join(EVAL_DIR, "cases.jsonl")
OUTPUTS_PATH = os.path.join(EVAL_DIR, "outputs.jsonl")
RUNS_DIR = os.path.join(EVAL_DIR, "judge_runs")
LABEL_ORDER_SEED = 20260916     # labelling order is shuffled so modes don't arrive in blocks

RULE = "=" * 78

MODE_KEYS = {
    "citation printed in brackets the citation checker cannot parse": "M1",
    "denial text that cannot be pasted into a letter as written": "M2",
    "widens a narrowly scoped clause into a general rule": "M3",
    "answers a corpus-wide question from one endorsement only": "M4",
    "cites a clause number that does not exist in the form it names": "M5",
    "refuses although the answering exclusion row is in the corpus": "M6",
}


# ---------------------------------------------------------------------------
# files
# ---------------------------------------------------------------------------

def load_jsonl(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def load_cases() -> list[dict]:
    return load_jsonl(CASES_PATH)


def load_outputs() -> dict[str, dict]:
    return {o["case_id"]: o for o in load_jsonl(OUTPUTS_PATH)}


def save_outputs(outputs: dict[str, dict], cases: list[dict]) -> None:
    order = [c["case_id"] for c in cases]
    with open(OUTPUTS_PATH, "w", encoding="utf-8") as fh:
        for cid in order:
            if cid in outputs:
                fh.write(json.dumps(outputs[cid], ensure_ascii=False) + "\n")


def load_labels() -> dict:
    if not os.path.exists(LABELS_PATH):
        return {}
    with open(LABELS_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def run_path(version: str) -> str:
    return os.path.join(RUNS_DIR, f"judge_{version}.json")


def load_run(version: str) -> dict | None:
    path = run_path(version)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def judge_versions() -> list[str]:
    """Runnable judge versions on disk, oldest first. v0 is the pre-split rubric and never runs."""
    found = []
    for name in os.listdir(EVAL_DIR):
        m = re.fullmatch(r"judge_(v(\d+))\.txt", name)
        if m and int(m.group(2)) >= 1:
            found.append((int(m.group(2)), m.group(1)))
    return [v for _, v in sorted(found)]


def judge_inputs(case: dict, out: dict) -> tuple[str, list[str]]:
    """What the judge (and the human) reads: the adjuster's input and the policy's forms."""
    if case["kind"] == "summary":
        return "ADJUSTER NOTES:\n" + out["notes_redacted"], case["policy_forms"]
    return "ADJUSTER QUESTION:\n" + out["question"], out["policy_forms"]


# ---------------------------------------------------------------------------
# generate — freeze the outputs everything downstream grades
# ---------------------------------------------------------------------------

def generate(cases: list[dict], force: bool = False, only: set[str] | None = None) -> dict:
    outputs = load_outputs()
    todo = [c for c in cases
            if (force or c["case_id"] not in outputs) and (not only or c["case_id"] in only)]
    if todo and os.path.isdir(RUNS_DIR) and os.listdir(RUNS_DIR) and force:
        sys.exit("refusing --force: a judge has already graded these outputs; regenerating "
                 "would orphan the hand labels")
    for i, case in enumerate(todo, 1):
        print(f"  [{i}/{len(todo)}] generating {case['case_id']} ({case['kind']})", flush=True)
        if case["kind"] == "summary":
            from summarizer import summarize_claim
            out = {"case_id": case["case_id"], "kind": "summary", **summarize_claim(case["notes"])}
        else:
            out = replay_regression(case)
        outputs[case["case_id"]] = out
        save_outputs(outputs, cases)
    return outputs


def replay_regression(case: dict) -> dict:
    """Rebuild the failed trace's request verbatim (Week 5 replay) and run it again."""
    from replay import build_messages, rebuild_context, sha
    from summarizer import sha16
    from tracing import call_model

    traces = {t["trace_id"]: t for t in load_jsonl(os.path.join(HERE, case["source_log"]))}
    trace = traces[case["source_trace_id"]]
    context, problems = rebuild_context(trace)
    messages, provenance = build_messages(trace, context)
    model = trace["model"]
    response, latency_ms = call_model(messages, model=model["name"],
                                      temperature=model["temperature"],
                                      max_tokens=model["max_tokens"])
    replayed = (response.choices[0].message.content or "").strip()
    return {
        "case_id": case["case_id"],
        "kind": "regression",
        "source_trace_id": trace["trace_id"],
        "question": trace["question"],
        "policy_forms": sorted({h["form_number"] for h in trace["retrieval"]["hits"]}),
        "replay_problems": problems,
        "replay_provenance": provenance,
        "rebuilt_prompt_sha256": sha(messages[0]["content"] + messages[1]["content"])[:16],
        "original_output": trace["output"]["raw"],
        "output": replayed,
        "output_sha256": sha16(replayed),
        "identical_to_trace": replayed == trace["output"]["raw"],
        "latency_ms": latency_ms,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }


# ---------------------------------------------------------------------------
# label — blind hand labels, before any judge output exists
# ---------------------------------------------------------------------------

def label_order(cases: list[dict]) -> list[str]:
    ids = sorted(c["case_id"] for c in cases if c["kind"] == "summary")
    random.Random(LABEL_ORDER_SEED).shuffle(ids)
    return ids


def _refuse_if_judged() -> None:
    if os.path.isdir(RUNS_DIR) and any(f.endswith(".json") for f in os.listdir(RUNS_DIR)):
        sys.exit("a judge run already exists in evals/judge_runs/ — labels written now "
                 "would not be blind. Labelling is closed.")


def _new_labels_doc(cases, outputs) -> dict:
    return {
        "protocol": ("Hand labels on the judge's single binary criterion, written BEFORE "
                     "any judge run. Labeller saw: criterion, adjuster input, full policy "
                     "wording, the output. Labeller did NOT see: failure-mode tag, assertion "
                     "results, any judge verdict."),
        "criterion_from": "evals/judge_v1.txt",
        "criterion": criterion_text("v1"),
        "labeller": None,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "finished_at": None,
        "order_seed": LABEL_ORDER_SEED,
        "labels": {
            cid: {"output_sha256": outputs[cid]["output_sha256"], "label": None,
                  "note": "", "labelled_at": None}
            for cid in label_order(cases)
        },
    }


def _write_labels(doc: dict) -> None:
    done = sum(1 for l in doc["labels"].values() if l["label"] in ("PASS", "FAIL"))
    if done == len(doc["labels"]) and not doc["finished_at"]:
        doc["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    with open(LABELS_PATH, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def _reading_view(case, out, n, total) -> str:
    input_text, forms = judge_inputs(case, out)
    return "\n".join([
        RULE, f"SUMMARY {n}/{total}   case {case['case_id']}   policy forms: {', '.join(forms)}", RULE,
        input_text, "", "--- POLICY WORDING " + "-" * 59, policy_wording(forms), "",
        "--- OUTPUT TO GRADE " + "-" * 58, out["output"], RULE,
    ])


def cmd_label(args) -> None:
    _refuse_if_judged()
    cases = {c["case_id"]: c for c in load_cases()}
    outputs = load_outputs()
    missing = [cid for cid in label_order(list(cases.values())) if cid not in outputs]
    if missing:
        sys.exit(f"outputs missing for {missing} — run `python week6_eval.py generate` first")

    doc = load_labels() or _new_labels_doc(list(cases.values()), outputs)
    if args.labeller:
        doc["labeller"] = args.labeller

    print(RULE + "\nCRITERION (the only thing you are grading)\n" + RULE)
    print(doc["criterion"])
    ids = list(doc["labels"])
    for n, cid in enumerate(ids, 1):
        entry = doc["labels"][cid]
        if entry["label"] in ("PASS", "FAIL"):
            continue
        print("\n" + _reading_view(cases[cid], outputs[cid], n, len(ids)))
        while True:
            answer = input("COVERAGE_SUPPORTED?  [p]ass / [f]ail / [s]kip / [q]uit > ").strip().lower()
            if answer in ("p", "f", "s", "q"):
                break
        if answer == "q":
            break
        if answer == "s":
            continue
        entry["label"] = "PASS" if answer == "p" else "FAIL"
        entry["note"] = input("one-line note (why), enter to skip > ").strip()
        entry["labelled_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        _write_labels(doc)

    _write_labels(doc)
    done = sum(1 for l in doc["labels"].values() if l["label"] in ("PASS", "FAIL"))
    print(f"\n{done}/{len(ids)} labelled -> {os.path.relpath(LABELS_PATH, HERE)}")
    if done == len(ids):
        print("Next: git add evals/labels_25.json && git commit -m 'week 6: blind labels'  "
              "(BEFORE any judge run)")


def cmd_packet(args) -> None:
    """A markdown reading packet plus a blank labels file, for labelling in an editor."""
    _refuse_if_judged()
    cases = {c["case_id"]: c for c in load_cases()}
    outputs = load_outputs()
    doc = load_labels() or _new_labels_doc(list(cases.values()), outputs)
    ids = list(doc["labels"])
    parts = ["# Week 6 labelling packet\n",
             "Grade each output on the criterion below. Record PASS or FAIL (and a one-line "
             "note) in `evals/labels_25.json`, then commit that file before any judge run.\n",
             "```\n" + doc["criterion"] + "\n```\n"]
    for n, cid in enumerate(ids, 1):
        parts.append("```\n" + _reading_view(cases[cid], outputs[cid], n, len(ids)) + "\n```\n")
    path = os.path.join(EVAL_DIR, "labelling_packet.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts))
    if not os.path.exists(LABELS_PATH):
        _write_labels(doc)
    print(f"packet : {os.path.relpath(path, HERE)}\nlabels : {os.path.relpath(LABELS_PATH, HERE)}")


# ---------------------------------------------------------------------------
# judge — only after the labels are committed
# ---------------------------------------------------------------------------

def run_judge(version: str, cases: list[dict], outputs: dict, only: set[str] | None = None) -> dict:
    evidence = labels_commit()                       # raises BlindProtocolError
    os.makedirs(RUNS_DIR, exist_ok=True)
    sha = template_sha(version)
    run = load_run(version) or {
        "judge_version": version,
        "judge_prompt_file": f"evals/judge_{version}.txt",
        "judge_prompt_sha256": sha,
        "labels_evidence": evidence,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "verdicts": {},
    }
    if run["labels_evidence"]["commit"] != evidence["commit"]:
        sys.exit("labels_25.json has been re-committed since this judge run began — "
                 "moving the labels after seeing verdicts is not allowed")
    if run["judge_prompt_sha256"] != sha:
        sys.exit(f"judge_{version}.txt changed after its run began "
                 f"({run['judge_prompt_sha256']} -> {sha}); write a new version instead")

    from answerer import MODEL
    run["model"] = {"name": MODEL, "temperature": 0.0}
    todo = [c for c in cases
            if (not only or c["case_id"] in only)
            and run["verdicts"].get(c["case_id"], {}).get("output_sha256")
            != outputs[c["case_id"]]["output_sha256"]]
    for i, case in enumerate(todo, 1):
        cid = case["case_id"]
        print(f"  [{i}/{len(todo)}] judge {version} -> {cid}", flush=True)
        input_text, forms = judge_inputs(case, outputs[cid])
        verdict = judge_one(version, input_text, forms, outputs[cid]["output"])
        run["verdicts"][cid] = {"output_sha256": outputs[cid]["output_sha256"],
                                "judged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), **verdict}
        run["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        with open(run_path(version), "w", encoding="utf-8") as fh:
            json.dump(run, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
    return run


def cmd_judge(args) -> None:
    cases = load_cases()
    outputs = load_outputs()
    only = None
    if args.labelled_only:
        only = set(load_labels().get("labels", {}))
    try:
        run = run_judge(args.version, cases, outputs, only)
    except BlindProtocolError as exc:
        sys.exit(f"BLIND PROTOCOL: {exc}")
    ev = run["labels_evidence"]
    print(f"\njudge {args.version}: {len(run['verdicts'])} verdicts -> {os.path.relpath(run_path(args.version), HERE)}")
    print(f"labels committed first: {ev['commit'][:10]} at {ev['commit_time']}; "
          f"judge run started {run['started_at']}")


# ---------------------------------------------------------------------------
# agreement — judge vs hand labels
# ---------------------------------------------------------------------------

def fewshot_case_ids(version: str) -> set[str]:
    with open(judge_path(version), encoding="utf-8") as fh:
        return set(re.findall(r"case_id:\s*(\w+)", fh.read()))


def agreement(version: str) -> dict:
    labels = load_labels()["labels"]
    run = load_run(version)
    if run is None:
        sys.exit(f"no judge run for {version} — python week6_eval.py judge --version {version}")
    outputs = load_outputs()
    shots = fewshot_case_ids(version)
    if labels_commit()["commit"] != run["labels_evidence"]["commit"]:
        sys.exit("labels_25.json changed after this judge run — agreement would measure a moved ruler")

    rows = []
    for cid, lab in labels.items():
        v = run["verdicts"].get(cid)
        if v is None:
            sys.exit(f"judge {version} has no verdict for labelled case {cid}")
        if len({lab["output_sha256"], outputs[cid]["output_sha256"], v["output_sha256"]}) != 1:
            sys.exit(f"{cid}: label, output and verdict do not refer to the same text")
        rows.append({"case_id": cid, "human": lab["label"], "judge": v["verdict"],
                     "agree": lab["label"] == v["verdict"], "human_note": lab["note"],
                     "judge_reason": v["reason"], "fewshot_example": cid in shots})

    def pct(rs):
        return round(100 * sum(r["agree"] for r in rs) / len(rs), 1) if rs else None

    held_out = [r for r in rows if not r["fewshot_example"]]
    conf = defaultdict(int)
    for r in rows:
        conf[f"human_{r['human']}__judge_{r['judge']}"] += 1
    result = {
        "judge_version": version,
        "n": len(rows),
        "agreement_pct": pct(rows),
        "agree": sum(r["agree"] for r in rows),
        "fewshot_case_ids": sorted(shots),
        "held_out_n": len(held_out),
        "held_out_agreement_pct": pct(held_out),
        "confusion": dict(conf),
        "disagreements": [r for r in rows if not r["agree"]],
    }
    with open(os.path.join(EVAL_DIR, f"agreement_{version}.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return result


def cmd_agreement(args) -> None:
    r = agreement(args.version)
    print(RULE)
    print(f"judge {r['judge_version']} vs hand labels: {r['agree']}/{r['n']} = {r['agreement_pct']}%")
    if r["fewshot_case_ids"]:
        print(f"held out (excluding few-shot examples {', '.join(r['fewshot_case_ids'])}): "
              f"{r['held_out_agreement_pct']}% over {r['held_out_n']}")
    print(f"confusion: {r['confusion']}")
    print(RULE)
    for d in r["disagreements"]:
        tag = "  [few-shot example]" if d["fewshot_example"] else ""
        print(f"{d['case_id']}: human {d['human']} / judge {d['judge']}{tag}")
        print(f"   human : {d['human_note'] or '(no note)'}")
        print(f"   judge : {d['judge_reason']}")


# ---------------------------------------------------------------------------
# run — the one command
# ---------------------------------------------------------------------------

def cmd_run(args) -> None:
    cases = load_cases()
    print(f"{len(cases)} cases: {sum(c['kind'] == 'summary' for c in cases)} summaries, "
          f"{sum(c['kind'] == 'regression' for c in cases)} regression replays of failed traces\n")

    outputs = load_outputs() if args.no_generate else generate(cases)
    missing = [c["case_id"] for c in cases if c["case_id"] not in outputs]
    if missing:
        sys.exit(f"no outputs for {missing}")

    version = args.judge or (judge_versions() or [None])[-1]
    run, judge_note = None, "judge not run (--no-judge)"
    if not args.no_judge and version:
        try:
            run = run_judge(version, cases, outputs)
            judge_note = f"judge {version} (labels commit {run['labels_evidence']['commit'][:10]})"
        except BlindProtocolError as exc:
            judge_note = f"judge SKIPPED — blind protocol: {exc}"

    per_case = []
    for c in cases:
        cid = c["case_id"]
        res = run_assertions(c, outputs[cid]["output"])
        applied = [r for r in res.values() if r["applies"]]
        a_pass = all(r["passed"] for r in applied)
        verdict = run["verdicts"].get(cid, {}).get("verdict") if run else None
        j_pass = None if verdict is None else verdict == "PASS"
        overall = a_pass and (j_pass if j_pass is not None else True)
        per_case.append({"case": c, "assertions": res, "a_pass": a_pass,
                         "verdict": verdict, "j_pass": j_pass, "pass": overall})

    names = list(ASSERTIONS)
    print(RULE + "\nPER CASE\n" + RULE)
    print(f"{'case':<5} {'mode':<4} {'kind':<10} " + " ".join(f"A{i+1}" for i in range(len(names)))
          + "  judge  PASS")
    for row in per_case:
        cells = []
        for n in names:
            r = row["assertions"][n]
            cells.append(" . " if not r["applies"] else (" ok" if r["passed"] else " XX"))
        print(f"{row['case']['case_id']:<5} {MODE_KEYS[row['case']['mode']]:<4} "
              f"{row['case']['kind']:<10}" + "".join(cells)
              + f"  {row['verdict'] or '-':<6} {'PASS' if row['pass'] else 'FAIL'}")

    failures = [(row["case"]["case_id"], n, row["assertions"][n]["detail"])
                for row in per_case for n in names
                if row["assertions"][n]["applies"] and not row["assertions"][n]["passed"]]
    if failures:
        print("\nassertion failures:")
        for cid, n, detail in failures:
            print(f"  {cid} {n.split('_')[0]}: {detail}")

    print("\n" + RULE + "\nPASS RATE BY MODE   (" + judge_note + ")\n" + RULE)
    print(f"| mode | {'name':<62} | n | assertions | judge | pass | pass % |")
    print(f"|------|{'-' * 64}|---|------------|-------|------|--------|")
    by_mode = defaultdict(list)
    for row in per_case:
        by_mode[row["case"]["mode"]].append(row)
    for mode, key in MODE_KEYS.items():
        rows = by_mode.get(mode, [])
        if not rows:
            continue
        judged = [r for r in rows if r["j_pass"] is not None]
        j = f"{sum(r['j_pass'] for r in judged)}/{len(judged)}" if judged else "-"
        p = sum(r["pass"] for r in rows)
        print(f"| {key:<4} | {mode:<62} | {len(rows)} | {sum(r['a_pass'] for r in rows):>4}/{len(rows):<5} "
              f"| {j:>5} | {p:>2}/{len(rows):<2}| {100 * p / len(rows):>5.0f}% |")
    total = sum(r["pass"] for r in per_case)
    print(f"\noverall {total}/{len(per_case)} = {100 * total / len(per_case):.0f}%   "
          f"(read the modes, not this line)")
    reg = [r for r in per_case if r["case"]["kind"] == "regression"]
    print(f"regression replays passing: {sum(r['pass'] for r in reg)}/{len(reg)}")

    print("\n" + RULE + "\nCRITERIA SPLIT\n" + RULE)
    for i, n in enumerate(names, 1):
        applied = [r["assertions"][n] for r in per_case if r["assertions"][n]["applies"]]
        print(f"  assertion A{i} {n[3:]:<28} {sum(a['passed'] for a in applied):>2}/{len(applied)} pass")
    print(f"  judged     COVERAGE_SUPPORTED           "
          + (f"{sum(1 for r in per_case if r['j_pass'])}/{sum(1 for r in per_case if r['j_pass'] is not None)} pass"
             if run else "not run"))
    print(f"\n  {len(names)} deterministic assertions vs 1 judged criterion "
          f"(judge_v0 graded all 6; judge_v1 grades 1)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--judge", default=None, help="judge version for the default run (default: latest)")
    ap.add_argument("--no-judge", action="store_true")
    ap.add_argument("--no-generate", action="store_true")
    sub = ap.add_subparsers(dest="cmd")

    s = sub.add_parser("generate", help="produce and freeze outputs for every case")
    s.add_argument("--force", action="store_true")
    s.add_argument("--only", nargs="*")
    s.set_defaults(func=lambda a: generate(load_cases(), a.force, set(a.only or [])))

    s = sub.add_parser("label", help="interactive blind labelling of the 25 summaries")
    s.add_argument("--labeller", default=None)
    s.set_defaults(func=cmd_label)

    s = sub.add_parser("packet", help="write a reading packet + blank labels file")
    s.set_defaults(func=cmd_packet)

    s = sub.add_parser("judge", help="run one judge version (guarded by the labels commit)")
    s.add_argument("--version", required=True)
    s.add_argument("--labelled-only", action="store_true")
    s.set_defaults(func=cmd_judge)

    s = sub.add_parser("agreement", help="judge vs hand labels, as a percentage")
    s.add_argument("--version", required=True)
    s.set_defaults(func=cmd_agreement)

    args = ap.parse_args()
    if args.cmd is None:
        cmd_run(args)
    else:
        args.func(args)


if __name__ == "__main__":
    main()
