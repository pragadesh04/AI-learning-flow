#!/usr/bin/env python3
"""
week10_race.py — Week 10: the claims squad vs the single agent, same 10 Week-6 cases.

    python week10_race.py                      # run both arms (cached), judge, write tables
    python week10_race.py --arm single         # one arm only
    python week10_race.py --inject-500 s05     # exclusions worker returns 500 on one case
    python week10_race.py --no-run             # score from the cached runs only

The ruler is the Week-6 one, unchanged: the five deterministic assertions in
src/assertions.py plus judge_v1's single COVERAGE_SUPPORTED criterion. A case
passes when every applicable assertion passes AND the judge says PASS — the
same rule week6_eval.py applies. The ten cases are drawn from the 25 Week-6
summary cases by a seeded, mode-stratified sample; none were written for this
week. (The 4 Week-6 regression cases are Q&A replays with no claim file, so
neither arm can run them.)

Judge tokens are the eval's cost, not either system's, and are reported apart.
Run records are cached in week10/{arm}_runs.jsonl; --force re-runs the model.
"""

import argparse
import json
import math
import os
import random
import statistics
import sys
from collections import defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv

load_dotenv()

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "src"))

from agent_loop import USD_PER_MTOK_COMPLETION, USD_PER_MTOK_PROMPT
from assertions import run_assertions
from judge import judge_one
from squad import run_single, run_squad
from tracing import DailyTokenLimit

OUT = os.path.join(HERE, "week10")
CASES_PATH = os.path.join(HERE, "evals", "cases.jsonl")
SELECTION_SEED = 20261012
N_CASES = 10
JUDGE_VERSION = "v1"
ARMS = {"single": run_single, "squad": run_squad}
RULE = "=" * 78


# ---------------------------------------------------------------------------
# the ten cases
# ---------------------------------------------------------------------------

def select_cases() -> list[dict]:
    """Seeded, mode-stratified: each mode gets its share of 10 by largest remainder."""
    cases = [json.loads(l) for l in open(CASES_PATH, encoding="utf-8") if l.strip()]
    pool = [c for c in cases if c["kind"] == "summary"]
    by_mode = defaultdict(list)
    for c in pool:
        by_mode[c["mode"]].append(c)
    quota = {m: N_CASES * len(cs) / len(pool) for m, cs in by_mode.items()}
    take = {m: int(q) for m, q in quota.items()}
    for m in sorted(quota, key=lambda m: (quota[m] - take[m], m), reverse=True):
        if sum(take.values()) == N_CASES:
            break
        take[m] += 1
    rng = random.Random(SELECTION_SEED)
    chosen = []
    for m in sorted(by_mode):
        chosen += rng.sample(sorted(by_mode[m], key=lambda c: c["case_id"]), take[m])
    return sorted(chosen, key=lambda c: c["case_id"])


# ---------------------------------------------------------------------------
# run cache
# ---------------------------------------------------------------------------

def runs_path(arm: str) -> str:
    return os.path.join(OUT, f"{arm}_runs.jsonl")


def load_runs(arm: str) -> dict:
    path = runs_path(arm)
    if not os.path.exists(path):
        return {}
    out = {}
    for line in open(path, encoding="utf-8"):
        if line.strip():
            rec = json.loads(line)
            out[rec["case_id"]] = rec
    return out


def save_runs(arm: str, runs: dict, order: list[str]) -> None:
    os.makedirs(OUT, exist_ok=True)
    with open(runs_path(arm), "w", encoding="utf-8") as fh:
        for cid in order:
            if cid in runs:
                fh.write(json.dumps(runs[cid], ensure_ascii=False) + "\n")


def grade(case: dict, rec: dict) -> None:
    """Week-6 assertions + judge_v1, written into the record (judge cached)."""
    rec["assertions"] = run_assertions(case, rec["output"])
    if rec.get("judge", {}).get("output") != rec["output"]:
        v = judge_one(JUDGE_VERSION, "ADJUSTER NOTES:\n" + rec["notes_redacted"],
                      case["policy_forms"], rec["output"])
        rec["judge"] = {"version": JUDGE_VERSION, "output": rec["output"], **v}
    applied = [a for a in rec["assertions"].values() if a["applies"]]
    rec["a_pass"] = all(a["passed"] for a in applied)
    rec["j_pass"] = rec["judge"]["verdict"] == "PASS"
    rec["pass"] = rec["a_pass"] and rec["j_pass"]


def warm_up() -> None:
    """Load the embedding model and BM25 index before the clock starts: the first
    search_policy call otherwise charges ~50s of cold start to whichever arm runs first."""
    from hybrid import fused_search
    fused_search("warm up", strategy="structure_aware", n_results=1)


def run_arm(arm: str, cases: list[dict], force: bool, fail_worker: str | None = None) -> dict:
    warm_up()
    runs = {} if force else load_runs(arm)
    order = [c["case_id"] for c in cases]
    for i, case in enumerate(cases, 1):
        rec = runs.get(case["case_id"])
        try:
            if rec is None:
                print(f"  [{arm} {i}/{len(cases)}] {case['case_id']} running", flush=True)
                rec = (run_squad(case, fail_worker=fail_worker) if fail_worker
                       else ARMS[arm](case))
                runs[case["case_id"]] = rec
                save_runs(arm, runs, order)
            if "pass" not in rec or rec.get("judge", {}).get("output") != rec["output"]:
                print(f"  [{arm} {i}/{len(cases)}] {case['case_id']} judging", flush=True)
                grade(case, rec)
                save_runs(arm, runs, order)
        except DailyTokenLimit as exc:
            sys.exit(f"\nSTOPPED: {exc}\nCached runs are kept; re-run the same command later.")
    return runs


# ---------------------------------------------------------------------------
# the numbers
# ---------------------------------------------------------------------------

def p_nearest(values: list[float], p: float) -> float:
    s = sorted(values)
    return s[max(0, math.ceil(p * len(s)) - 1)]


def arm_numbers(runs: list[dict]) -> dict:
    lat = [r["latency_s"] for r in runs]
    tokens = sum(r["total_tokens"] for r in runs)
    return {
        "n": len(runs),
        "passed": sum(r["pass"] for r in runs),
        "pass_rate": 100 * sum(r["pass"] for r in runs) / len(runs),
        "p50": statistics.median(lat),
        "p99": p_nearest(lat, 0.99),
        "tokens": tokens,
        "cost_per_claim": sum(r["cost_usd"] for r in runs) / len(runs),
        "a_pass": sum(r["a_pass"] for r in runs),
        "j_pass": sum(r["j_pass"] for r in runs),
    }


def handoff_shares(runs: list[dict]) -> dict:
    by = defaultdict(lambda: {"calls": 0, "prompt": 0, "completion": 0, "total": 0})
    for r in runs:
        for c in r["calls"]:
            h = by[c["handoff"]]
            h["calls"] += 1
            h["prompt"] += c["prompt_tokens"]
            h["completion"] += c["completion_tokens"]
            h["total"] += c["total_tokens"]
    return dict(by)


def write_handoffs_log(cases, single, squad) -> str:
    lines = ["# week10/handoffs.log — every model call, tagged with the hand-off that caused it.",
             "# tokens are metered response.usage, summed per hand-off per case.",
             "# columns: case arm handoff calls prompt_tok completion_tok total_tok share_of_case",
             ""]
    for c in cases:
        cid = c["case_id"]
        for arm, runs in (("single", single), ("squad", squad)):
            rec = runs[cid]
            per = defaultdict(lambda: [0, 0, 0, 0])
            for call in rec["calls"]:
                p = per[call["handoff"]]
                p[0] += 1
                p[1] += call["prompt_tokens"]
                p[2] += call["completion_tokens"]
                p[3] += call["total_tokens"]
            for h, (n, pt, ct, tt) in per.items():
                lines.append(f"{cid}  {arm:<6}  {h:<34} calls={n:<2} prompt={pt:<6} "
                             f"completion={ct:<5} total={tt:<6} "
                             f"share={100 * tt / max(1, rec['total_tokens']):5.1f}%")
            lines.append(f"{cid}  {arm:<6}  {'TOTAL':<34} calls={len(rec['calls']):<2} "
                         f"{'':<34}total={rec['total_tokens']}")
        lines.append("")
    path = os.path.join(OUT, "handoffs.log")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return path


def write_race_table(cases, single, squad) -> str:
    s_runs = [single[c["case_id"]] for c in cases]
    m_runs = [squad[c["case_id"]] for c in cases]
    s, m = arm_numbers(s_runs), arm_numbers(m_runs)
    mult = m["tokens"] / s["tokens"]
    shares = handoff_shares(m_runs)
    top_name, top = max(shares.items(), key=lambda kv: kv[1]["total"])
    crit = [r["critical_path_s"] for r in m_runs]

    def money(x):
        return f"${x:.6f}"

    out = [
        "# Week 10 race — single agent vs claims squad",
        "",
        f"Same 10 Week-6 summary cases (seeded stratified sample, seed {SELECTION_SEED}): "
        + ", ".join(c["case_id"] for c in cases) + ".",
        f"Same ruler: 5 Week-6 assertions + judge_{JUDGE_VERSION} (COVERAGE_SUPPORTED); "
        "pass = all applicable assertions pass AND judge PASS.",
        f"Same model ({s_runs[0]['model']['name']}, temperature 0), same search_policy tool, "
        "same budget ledger.",
        "",
        "| metric | single agent | squad (orchestrator + 2 workers) |",
        "|---|---|---|",
        f"| pass rate | {s['passed']}/{s['n']} = {s['pass_rate']:.0f}% | "
        f"{m['passed']}/{m['n']} = {m['pass_rate']:.0f}% |",
        f"| p50 latency (s) | {s['p50']:.2f} | {m['p50']:.2f} |",
        f"| p99 latency (s) | {s['p99']:.2f} | {m['p99']:.2f} |",
        f"| total tokens (10 claims) | {s['tokens']:,} | {m['tokens']:,} |",
        f"| cost per claim | {money(s['cost_per_claim'])} | {money(m['cost_per_claim'])} |",
        "",
        f"**Context re-send multiplier: {m['tokens']:,} / {s['tokens']:,} = {mult:.1f}x.** "
        f"Largest token share: `{top_name}`, {top['total']:,} tokens = "
        f"{100 * top['total'] / m['tokens']:.0f}% of all squad tokens.",
        "",
        "Squad tokens by hand-off (all 10 cases):",
        "",
        "| hand-off | calls | prompt | completion | total | share |",
        "|---|---|---|---|---|---|",
    ]
    for name, h in sorted(shares.items(), key=lambda kv: -kv[1]["total"]):
        out.append(f"| {name} | {h['calls']} | {h['prompt']:,} | {h['completion']:,} | "
                   f"{h['total']:,} | {100 * h['total'] / m['tokens']:.0f}% |")
    out += [
        "",
        "Per case:",
        "",
        "| case | mode | single: assertions / judge / PASS | tokens | latency s "
        "| squad: assertions / judge / PASS | tokens | latency s |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for c in cases:
        a, b = single[c["case_id"]], squad[c["case_id"]]

        def cell(r):
            failed = [k.split("_")[0] for k, v in r["assertions"].items()
                      if v["applies"] and not v["passed"]]
            return (f"{'ok' if r['a_pass'] else 'XX ' + ','.join(failed)} / "
                    f"{r['judge']['verdict']} / {'PASS' if r['pass'] else 'FAIL'}")
        out.append(f"| {c['case_id']} | {c['mode'][:38]} | {cell(a)} | {a['total_tokens']:,} | "
                   f"{a['latency_s']:.2f} | {cell(b)} | {b['total_tokens']:,} | {b['latency_s']:.2f} |")
    out += [
        "",
        "Notes on the numbers:",
        "",
        f"- Latency is summed model time + tool time as executed (the Week-7 work clock); the "
        f"provider's rate-limit queue is excluded. The squad ran its two workers one after the "
        f"other; if they ran concurrently its critical path would be p50 "
        f"{statistics.median(crit):.2f}s / p99 {p_nearest(crit, 0.99):.2f}s.",
        "- p99 over 10 runs is nearest-rank, i.e. the slowest run. It is reported because "
        "the slowest claim is the one that gets complained about.",
        f"- Cost uses the notional tariff from Week 7 (${USD_PER_MTOK_PROMPT}/Mtok prompt, "
        f"${USD_PER_MTOK_COMPLETION}/Mtok completion) on metered tokens; Groq's free tier bills $0.",
        f"- Assertions passed: single {s['a_pass']}/10, squad {m['a_pass']}/10. "
        f"Judge PASS: single {s['j_pass']}/10, squad {m['j_pass']}/10.",
        "- Judge calls are the eval's cost and are in neither arm's tokens.",
    ]
    path = os.path.join(OUT, "race_table.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")
    print("\n".join(out))
    return path


def write_failure_raw(case: dict, rec: dict) -> str:
    failed = [k for k, v in rec["assertions"].items() if v["applies"] and not v["passed"]]
    out = [
        f"# Injected failure — raw record ({case['case_id']}, {case['claim_number']})",
        "",
        "Fault: `orchestrator->exclusions_worker` raises HTTP 500 on every attempt "
        "(`run_squad(case, fail_worker='exclusions')`).",
        "",
        "Orchestrator events, in order:",
        "",
        *[f"- {e}" for e in rec["events"]],
        "",
        "What synthesis was handed as the exclusions report:",
        "",
        "```", rec["worker_reports"].get("exclusions", ""), "```",
        "",
        "Final output the claims handler would receive:",
        "",
        "```", rec["output"], "```",
        "",
        f"Graded with the same ruler: assertions {'all pass' if rec['a_pass'] else 'FAIL ' + ', '.join(failed)}; "
        f"judge_{JUDGE_VERSION} {rec['judge']['verdict']} — {rec['judge']['reason']}",
        "",
        f"Tokens {rec['total_tokens']:,}, latency {rec['latency_s']:.2f}s, "
        f"calls: {', '.join(c['handoff'] for c in rec['calls'])}",
    ]
    path = os.path.join(OUT, "failure_case_raw.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")
    print("\n".join(out))
    return path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arm", choices=list(ARMS))
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--no-run", action="store_true")
    ap.add_argument("--inject-500", metavar="CASE_ID")
    args = ap.parse_args()

    cases = select_cases()
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "selected_cases.json"), "w", encoding="utf-8") as fh:
        json.dump({"seed": SELECTION_SEED, "pool": "evals/cases.jsonl kind=summary (25)",
                   "case_ids": [c["case_id"] for c in cases],
                   "modes": {c["case_id"]: c["mode"] for c in cases}}, fh, indent=2)
    print(f"{len(cases)} cases (seed {SELECTION_SEED}): {', '.join(c['case_id'] for c in cases)}")

    if args.inject_500:
        case = next(c for c in cases if c["case_id"] == args.inject_500)
        runs = run_arm("squad_fail500", [case], args.force, fail_worker="exclusions")
        write_failure_raw(case, runs[case["case_id"]])
        return

    arms = [args.arm] if args.arm else list(ARMS)
    results = {}
    for arm in arms:
        results[arm] = load_runs(arm) if args.no_run else run_arm(arm, cases, args.force)
    if len(arms) == 2:
        missing = [c["case_id"] for c in cases
                   if any("pass" not in results[a].get(c["case_id"], {}) for a in arms)]
        if missing:
            sys.exit(f"incomplete: {missing} not run/judged in both arms")
        write_race_table(cases, results["single"], results["squad"])
        print("\n" + RULE)
        print("wrote", os.path.relpath(write_handoffs_log(cases, results["single"],
                                                          results["squad"]), HERE))


if __name__ == "__main__":
    main()
