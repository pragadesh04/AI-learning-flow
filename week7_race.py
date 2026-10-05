#!/usr/bin/env python3
"""
week7_race.py — Week 7: agent vs fixed workflow over the same ten claims.

One command each, per the submission checklist:

    python week7_race.py --system agent        # the loop, alone
    python week7_race.py --system workflow     # the hard-coded steps, alone
    python week7_race.py                       # the race -> week7/race.csv
    python week7_race.py --budget-demo         # one run that hits a budget and stops

Both arms are graded by the same function (`claims.grade_output`), the same
output contract, the same three tools and the same model. The only difference
is that one of them decides for itself what to do next.

Run records are cached in week7/{system}_runs.jsonl so a re-run of the scoring
costs no tokens; --force re-runs the model.
"""

import argparse
import csv
import json
import os
import statistics
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv

load_dotenv()

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "src"))

from agent_loop import BUDGET_NAMES, DEFAULT_BUDGETS, QUEUE_SUSPECT_S, \
    USD_PER_MTOK_COMPLETION, USD_PER_MTOK_PROMPT, run_agent
from claims import CASE_IDS, CLAIMS, EXPECTED, by_case, grade_output
from tracing import DailyTokenLimit
from workflow import run_workflow

OUT_DIR = os.path.join(HERE, "week7")
RUNS = {s: os.path.join(OUT_DIR, f"{s}_runs.jsonl") for s in ("agent", "workflow")}


def runs_path(name: str) -> str:
    """Cache file for an arm; Week 8 arms (agent_mitigated, ...) get their own."""
    return RUNS.get(name) or os.path.join(OUT_DIR, f"{name}_runs.jsonl")
RACE_CSV = os.path.join(OUT_DIR, "race.csv")
BUDGET_LOG = os.path.join(OUT_DIR, "budget_termination.log")

RULE = "=" * 78


# ---------------------------------------------------------------------------
# run records
# ---------------------------------------------------------------------------

def load_runs(system: str) -> dict:
    path = runs_path(system)
    if not os.path.exists(path):
        return {}
    out = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rec = json.loads(line)
                out[rec["case_id"]] = rec
    return out


def append_run(system: str, record: dict) -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(runs_path(system), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def run_arm(system: str, force: bool = False, only: set[str] | None = None,
            validate_payout_args: bool = False, suffix: str = "",
            sanitize: bool = False, output_guard: bool = False) -> dict:
    cached = {} if force else load_runs(system + suffix)
    runner = run_agent if system == "agent" else run_workflow
    for n, claim in enumerate(CLAIMS, 1):
        cid = claim["case_id"]
        if only and cid not in only:
            continue
        if cid in cached:
            continue
        print(f"  [{n}/{len(CLAIMS)}] {system}{suffix} {cid} {claim['claim_number']} "
              f"({len(cached)} cached)", flush=True)
        t0 = time.monotonic()
        try:
            if system == "agent":
                record = runner(claim, validate_payout_args=validate_payout_args,
                                sanitize=sanitize, output_guard=output_guard)
            else:
                record = runner(claim, validate_payout_args=validate_payout_args)
        except DailyTokenLimit as exc:
            # Every claim finished so far is already on disk, so the arm resumes
            # from where it stopped rather than from the beginning.
            print(f"\n{system}{suffix}: {len(cached)}/{len(CLAIMS)} claims saved to "
                  f"{os.path.relpath(runs_path(system + suffix), HERE)}\n{exc}\n"
                  f"re-run the same command after the reset to finish the arm.",
                  file=sys.stderr)
            raise
        record["wall_wallclock_s"] = round(time.monotonic() - t0, 1)
        cached[cid] = record
        append_run(system + suffix, record)
    return cached


# ---------------------------------------------------------------------------
# the four numbers
# ---------------------------------------------------------------------------

def p50(values: list[float]) -> float:
    return round(statistics.median(values), 3) if values else 0.0


def four_numbers(records: dict) -> dict:
    """Pass rate, p50 latency, total tokens, cost per claim. Nothing else."""
    rows = [grade_output(records[cid]["output"], by_case(cid))
            for cid in CASE_IDS if cid in records]
    if not rows:
        return {}
    latencies = [records[cid]["wall_clock_s"] for cid in CASE_IDS if cid in records]
    tokens = [records[cid]["usage"]["total_tokens"] for cid in CASE_IDS if cid in records]
    costs = [records[cid]["usage"]["cost_usd"] for cid in CASE_IDS if cid in records]
    laps = [records[cid]["usage"]["laps"] for cid in CASE_IDS if cid in records]
    calls = [len(records[cid]["trajectory"]) for cid in CASE_IDS if cid in records]
    return {
        "n": len(rows),
        "pass_rate_pct": round(100 * sum(r["pass"] for r in rows) / len(rows), 1),
        "p50_latency_s": p50(latencies),
        "total_tokens": sum(tokens),
        "cost_per_claim_usd": round(sum(costs) / len(costs), 6),
        # kept for the verdict paragraph, not part of the four
        "pass_count": sum(r["pass"] for r in rows),
        "mean_tokens": round(sum(tokens) / len(tokens), 1),
        "mean_laps": round(sum(laps) / len(laps), 2),
        "mean_tool_calls": round(sum(calls) / len(calls), 2),
        "budget_terminations": sum(1 for cid in CASE_IDS
                                   if cid in records and records[cid]["stop_reason"].startswith("budget")),
    }


# ---------------------------------------------------------------------------
# budget demo
# ---------------------------------------------------------------------------

def budget_demo() -> None:
    """
    Four runs, one per budget, and every one of them must stop.

    A single run with all four ceilings squeezed does not demonstrate four
    budgets; it demonstrates whichever ceiling happens to bite first, which on
    this claim is always the same one. So each run moves ONE budget and leaves
    the other three at the shipped allowance, and the log attributes the stop to
    the budget that caused it.

    The log is written after every run, not at the end, so a provider that runs
    out of daily tokens half way through leaves the completed ceilings on disk
    with an explicit note about which one did not run.

    Written to week7/budget_termination.log and printed.
    """
    runs = [
        ("max_iterations", "c05", {"max_iterations": 3},
         "c05 thrashes on search_policy; the iteration ceiling ends the thrash and the "
         "reserved final lap still produces a triage line"),
        ("max_tokens", "c04", {"max_tokens": 2_000},
         "the token ceiling is spent during the second search, so the wording is never "
         "finished reading"),
        ("max_cost_usd", "c04", {"max_cost_usd": 0.0005},
         "the notional spend ceiling trips at the same lap the token ceiling would have, "
         "which is the point: cost is a budget you can actually set per claim"),
        ("max_wall_clock_s", "c04", {"max_wall_clock_s": 4.0},
         "the work clock stops the run mid-search. NOTE: a non-streaming response has no "
         "time-to-first-token, so provider queueing cannot be separated from generation "
         "and is charged to the clock; the log prints the split so a reader can see how "
         "much of a fired clock was the throttle. See BudgetLedger.record()."),
    ]

    lines = [RULE, "BUDGET TERMINATION LOG — one budget at a time", RULE,
             f"shipped allowance   " + "  ".join(f"{k}={DEFAULT_BUDGETS[k]}"
                                                 for k in BUDGET_NAMES),
             "note                one budget moved per run; the other three stay at the "
             "shipped allowance.",
             "                    same three tools, same model, same prompt, same claim.",
             "termination         BudgetLedger.check() runs before AND after every lap, so a "
             "ceiling can",
                    "                    fire on the way in (a previous lap overspent) and on "
             "the way out (this",
                    "                    lap did). Either way the loop stops and names the "
             "budget. The model",
                    "                    is not called again afterwards.", ""]

    def flush(text: str) -> None:
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(BUDGET_LOG, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")

    for i, (name, case_id, override, why) in enumerate(runs):
        claim = by_case(case_id)
        budgets = {**DEFAULT_BUDGETS, **override}
        lines += [RULE,
                  f"BUDGET: {name}  ->  {case_id} {claim['claim_number']} "
                  f"({'/'.join(claim['policy_forms'])})",
                  RULE,
                  f"  budgets     " + "  ".join(f"{k}={budgets[k]}" for k in BUDGET_NAMES),
                  f"  why this number   {why}",
                  "",
                  f"  {'lap':>3}  {'tool':<15} {'args':<50} {'p_tok':>6} {'c_tok':>6} "
                  f"{'cum_tok':>8} {'cum_cost':>9} {'ms':>7}"]
        try:
            record = run_agent(claim, budgets=budgets)
        except DailyTokenLimit as exc:
            # The allowance is gone for the day, so every ceiling from here on is
            # unrun. Say so for all of them rather than leaving a partial file
            # that reads as if the rest were demonstrated.
            for pending, (pname, pcase, _, pwhy) in enumerate(runs[i:]):
                lines += ["", f"  NOT RUN   {pname} on {pcase}: {exc}" if pending == 0
                          else f"  NOT RUN   {pname} on {pcase}: skipped, the provider's daily "
                               f"allowance was already spent on an earlier ceiling above", ""]
            lines += ["Re-run `week7_race.py --budget-demo` after the provider's daily "
                      "allowance resets. The ceilings already shown above are unaffected.", ""]
            break
        for lap in record["laps"]:
            tools = ",".join(t["tool"] for t in lap["tool_calls"]) or "(final answer)"
            args = "; ".join(
                f"{k}={json.dumps(v, ensure_ascii=False)[:28]}"
                for t in lap["tool_calls"] for k, v in t["args"].items())
            lines.append(
                f"  {lap['lap']:>3}  {tools:<15} {args[:50]:<50} "
                f"{lap['prompt_tokens']:>6} {lap['completion_tokens']:>6} "
                f"{lap['cum_tokens']:>8} {lap['cum_cost_usd']:>9.6f} {lap['latency_ms']:>7.0f}")
        used = record["usage"]
        stopped = [s["budget"] for s in record["budget_stops"]]
        lines += [
            "",
            f"  stop_reason      {record['stop_reason']}",
            f"  budget fired     {', '.join(stopped) or '(none — the run answered first)'}",
        ]
        for stop in record["budget_stops"]:
            lines.append(f"    {stop['budget']}: {stop['detail']}")
        lines += [
            f"  laps run         {used['laps']} of {budgets['max_iterations']} allowed",
            f"  tokens           {used['total_tokens']} of {budgets['max_tokens']} allowed",
            f"  cost             ${used['cost_usd']:.6f} of ${budgets['max_cost_usd']} allowed",
            f"  work clock       {used['app_time_s']:.2f}s of {budgets['max_wall_clock_s']}s "
            f"allowed",
        ]
        if used["queue_suspect_s"]:
            lines += [
                f"    of which       {used['queue_suspect_s']:.2f}s is provider queueing, not "
                f"the loop:",
                f"                   laps {', '.join(str(s['lap']) for s in used['slow_laps'])} "
                f"each ran past {QUEUE_SUSPECT_S:.0f}s",
                f"    loop's own     {used['work_clock_s']:.2f}s of "
                f"{budgets['max_wall_clock_s']}s allowed",
                f"    a non-streaming response carries no time-to-first-token, so a call the "
                f"free",
                f"    tier queued looks exactly like a call that thought for the same length "
                f"of time.",
                f"    Read the ceiling against the loop's own number, not the total.",
            ]
        lines += [
            f"  tool calls made  {len(record['trajectory'])}  "
            f"({'->'.join(record['trajectory']) or 'none'})",
            "",
            "  what the handler gets back:",
        ]
        if record["output"].strip():
            lines += [f"    {ln}" for ln in record["output"].splitlines()]
        else:
            # The asymmetry is the point of the exercise and it is worth stating
            # in the log: the ITERATION ceiling still yields a verdict, because
            # its last lap is reserved for the answer. A token, cost or work
            # ceiling can bite on any lap, and there is then no budget left to
            # buy one, so the honest result is an untriaged claim.
            lines += ["    (empty — the budget stopped the loop before the model committed "
                      "to a verdict)",
                      "",
                      "    ESCALATE: this claim is untriaged and must go to a human adjuster.",
                      "    The budget is the reason, not the model. Compare the max_iterations",
                      "    section above: there the last lap is reserved for the answer, so the",
                      "    same system still returns a verdict. Spending tokens to manufacture one",
                      "    after a token budget has fired would defeat the budget that fired it."]
        lines.append("")
        flush("\n".join(lines))

    text = "\n".join(lines)
    flush(text)
    print(text)
    print(f"written to {os.path.relpath(BUDGET_LOG, HERE)}")


# ---------------------------------------------------------------------------
# the table
# ---------------------------------------------------------------------------

def write_csv(agent: dict, workflow: dict) -> None:
    a, w = four_numbers(agent), four_numbers(workflow)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(RACE_CSV, "w", encoding="utf-8", newline="") as fh:
        wtr = csv.writer(fh)
        wtr.writerow(["metric", "agent", "workflow", "winner"])
        rows = [
            ("claims_run", a["n"], w["n"], "tie"),
            ("pass_rate_pct", a["pass_rate_pct"], w["pass_rate_pct"],
             "agent" if a["pass_rate_pct"] > w["pass_rate_pct"] else
             "workflow" if w["pass_rate_pct"] > a["pass_rate_pct"] else "tie"),
            ("p50_latency_s", a["p50_latency_s"], w["p50_latency_s"],
             "agent" if a["p50_latency_s"] < w["p50_latency_s"] else
             "workflow" if w["p50_latency_s"] < a["p50_latency_s"] else "tie"),
            ("total_tokens", a["total_tokens"], w["total_tokens"],
             "agent" if a["total_tokens"] < w["total_tokens"] else
             "workflow" if w["total_tokens"] < a["total_tokens"] else "tie"),
            ("cost_per_claim_usd", a["cost_per_claim_usd"], w["cost_per_claim_usd"],
             "agent" if a["cost_per_claim_usd"] < w["cost_per_claim_usd"] else
             "workflow" if w["cost_per_claim_usd"] < a["cost_per_claim_usd"] else "tie"),
        ]
        wtr.writerows(rows)
        wtr.writerow([])
        wtr.writerow(["supporting", "agent", "workflow", ""])
        wtr.writerow(["mean_model_laps", a["mean_laps"], w["mean_laps"], ""])
        wtr.writerow(["mean_tool_calls", a["mean_tool_calls"], w["mean_tool_calls"], ""])
        wtr.writerow(["mean_tokens_per_claim", a["mean_tokens"], w["mean_tokens"], ""])
        wtr.writerow(["budget_terminations", a["budget_terminations"],
                      w["budget_terminations"], ""])
        wtr.writerow(["tariff_usd_per_mtok_prompt", USD_PER_MTOK_PROMPT,
                      USD_PER_MTOK_PROMPT, "notional; free tier bills 0"])


def print_table(agent: dict, workflow: dict) -> None:
    a, w = four_numbers(agent), four_numbers(workflow)
    print(RULE + "\nTHE RACE — same 10 claims, same 3 tools, same model, same contract\n" + RULE)
    print(f"| {'metric':<24} | {'agent':>12} | {'workflow':>12} | winner |")
    print(f"|{'-' * 26}|{'-' * 14}|{'-' * 14}|---------|")
    def row(label, av, wv, better, fmt="{}"):
        win = "agent" if better(av, wv) < 0 else "workflow" if better(av, wv) > 0 else "tie"
        print(f"| {label:<24} | {fmt.format(av):>12} | {fmt.format(wv):>12} | {win:<7} |")
    row("pass rate %", a["pass_rate_pct"], w["pass_rate_pct"], lambda x, y: (y > x) - (x > y))
    row("p50 latency s", a["p50_latency_s"], w["p50_latency_s"], lambda x, y: (x > y) - (x < y))
    row("total tokens", a["total_tokens"], w["total_tokens"], lambda x, y: (x > y) - (x < y))
    row("cost / claim $", a["cost_per_claim_usd"], w["cost_per_claim_usd"],
        lambda x, y: (x > y) - (x < y), "{:.5f}")
    print(f"|{'-' * 26}|{'-' * 14}|{'-' * 14}|---------|")
    print(f"| {'model laps / claim':<24} | {a['mean_laps']:>12} | {w['mean_laps']:>12} |")
    print(f"| {'tool calls / claim':<24} | {a['mean_tool_calls']:>12} | {w['mean_tool_calls']:>12} |")
    print(f"| {'budget terminations':<24} | {a['budget_terminations']:>12} | "
          f"{w['budget_terminations']:>12} |")
    print(f"\ncost priced at ${USD_PER_MTOK_PROMPT}/Mtok in + ${USD_PER_MTOK_COMPLETION}/Mtok out "
          f"(notional — the free tier bills $0.00)")

    print(RULE + "\nPER CLAIM\n" + RULE)
    print(f"| {'case':<5} {'claim':<16} | {'agent':<26} | {'workflow':<26} |")
    print(f"|{'-' * 7}|{'-' * 18}|{'-' * 28}|{'-' * 28}|")
    for cid in CASE_IDS:
        arow = grade_output(agent[cid]["output"], by_case(cid)) if cid in agent else None
        wrow = grade_output(workflow[cid]["output"], by_case(cid)) if cid in workflow else None
        at = f"{'PASS' if arow['pass'] else 'FAIL'} {agent[cid]['stop_reason'][:17]}" if arow else "-"
        wt = f"{'PASS' if wrow['pass'] else 'FAIL'} {workflow[cid]['stop_reason'][:17]}" if wrow else "-"
        print(f"| {cid:<5} {by_case(cid)['claim_number']:<16} | {at:<26} | {wt:<26} |")
    exp = {cid: EXPECTED[cid] for cid in CASE_IDS}
    print(f"\nground truth written from endorsements/ first: "
          + ", ".join(f"{c}={exp[c]['status']}/${exp[c]['payable_usd']}" for c in CASE_IDS))
    print(f"\n-> {os.path.relpath(RACE_CSV, HERE)}")


TOOL_DOC = os.path.join(OUT_DIR, "tool_descriptions.md")


def write_tool_doc() -> None:
    """
    The three descriptions and the third tool's diff.

    The diff is against the wording the third tool would have had if it had
    been written the way the first two are: a paragraph that names two jobs
    and hedges. `overlaps()` is the mechanical check the rubric asks for —
    a description that shares a job word with another tool's description is a
    description that will get the wrong tool called.
    """
    from agent_tools import TOOL_DESCRIPTIONS

    jobs = {"get_claim": ["claim", "notes", "record", "adjuster system"],
            "search_policy": ["wording", "endorsement", "clause", "peril", "policy"],
            "compute_payout": ["excess", "arithmetic", "money", "payable", "amount"]}
    lines = ["# Week 7 — the three tool descriptions\n",
             "`get_claim` and `search_policy` are the two the task hands you. The diff below "
             "is for the third one, which is the one the rubric scores: one job, an enum on "
             "the claim-status parameter, and no wording shared with the other two.\n",
             "## The third tool, and the diff\n",
             "```diff",
             "  # v1 — the first draft, the way the other two are written: two jobs, hedged",
             "  + \"Look up the claim and its exclusions, then work out how much is payable.",
             "  +  Useful when you need the claim details, the applicable exclusion codes and",
             "  +  the payment calculation together.\"",
             "- \"Apply one policy excess to one already-adjudicated covered amount and return",
             "-  the payable figure with the arithmetic. This tool returns money only. It does",
             "-  not read policy wording and it does not decide whether a loss is covered.\"",
             "```",
             "",
             "The v1 draft says \"claim\", \"exclusions\" and \"calculation\" in one sentence, "
             "so a model reading it has three reasons to reach for it at step one. The shipped "
             "version says what it does, and then says the two things it does not do, which "
             "is where the separation actually lives.\n",
             "## All three, as sent\n"]
    for name, desc in TOOL_DESCRIPTIONS.items():
        lines += [f"### `{name}`\n", "```", desc, "```", ""]

    lines += ["## Overlap check\n",
              "| description | job words | shared with another tool |", "|---|---|---|"]
    for name, desc in TOOL_DESCRIPTIONS.items():
        low = desc.lower()
        mine = [w for w in jobs[name] if w in low]
        shared = []
        for other, desc2 in TOOL_DESCRIPTIONS.items():
            if other == name:
                continue
            for w in jobs[other]:
                if w in low and w in desc2.lower():
                    shared.append(f"{w} (with {other})")
        lines.append(f"| `{name}` | {', '.join(mine)} | {', '.join(shared) or 'none'} |")

    lines += ["",
              "Read the middle column before reading the prose: the three descriptions DO share "
              "nouns,\nand deliberately so. Each one ends by naming what it does not do, and "
              "you cannot say\n\"it does not read policy wording\" without using the words "
              "policy and wording. The\noverlap that matters is not lexical, it is directional: "
              "a word that appears in a\ndescription followed by a *negation* is a word that "
              "pushes the model away. The\nonly genuinely shared noun is *amount*, which is "
              "the same word for two different\nnumbers (claimed vs payable), and the two "
              "sentences separate those by what\nthe tool does with the number rather than by "
              "the number itself. `compute_payout`\nis the only one of the three that "
              "subtracts anything.\n",
              "## The enum\n",
              "`compute_payout.claim_status` is a closed set of six workflow states:\n"]
    from agent_tools import CLAIM_STATUS_ENUM
    lines += [f"- `{s}`" for s in CLAIM_STATUS_ENUM]
    lines += ["",
              "They are workflow states, not triage verdicts. `PAY`/`DENY`/`REFER` are the "
              "output contract's business and appear nowhere in the tool's parameters, because "
              "a tool that accepts `denied` as an argument will be called with `denied` and "
              "the caller will stop thinking. A claim_status the enum does not contain is a "
              "week-8 argument-validity failure, and it is checked offline in "
              "`agent_tools.argument_problems`.\n"]
    with open(TOOL_DOC, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return TOOL_DOC


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--system", choices=["agent", "workflow", "both"], default="both")
    ap.add_argument("--force", action="store_true", help="re-run the model, ignore the cache")
    ap.add_argument("--only", nargs="*", help="case ids, e.g. c01 c04")
    ap.add_argument("--validate-payout-args", action="store_true",
                    help="the Week-8 mitigation switch; do not use for the Week-7 race")
    ap.add_argument("--sanitize", action="store_true",
                    help="Week-8 bonus defence D1: mask injected instructions in tool output")
    ap.add_argument("--output-guard", action="store_true",
                    help="Week-8 bonus defence D3: deterministic check on the final text")
    ap.add_argument("--suffix", default="", help="cache file suffix, used by Week 8")
    ap.add_argument("--budget-demo", action="store_true")
    args = ap.parse_args()

    if args.budget_demo:
        budget_demo()
        return

    only = set(args.only) if args.only else None
    systems = ["agent", "workflow"] if args.system == "both" else [args.system]
    records = {}
    for system in systems:
        print(f"running {system}{args.suffix} over {len(CLAIMS)} claims", flush=True)
        records[system] = run_arm(system, force=args.force, only=only,
                                  validate_payout_args=args.validate_payout_args,
                                  suffix=args.suffix, sanitize=args.sanitize,
                                  output_guard=args.output_guard)
        missing = [c for c in CASE_IDS if c not in records[system]]
        if missing:
            sys.exit(f"{system} has no run for {missing} — run it without --only first")

    if set(systems) == {"agent", "workflow"}:
        write_csv(records["agent"], records["workflow"])
        print_table(records["agent"], records["workflow"])
        print(f"-> {os.path.relpath(write_tool_doc(), HERE)}")


if __name__ == "__main__":
    main()
