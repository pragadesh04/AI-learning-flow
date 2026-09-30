#!/usr/bin/env python3
"""
dump_runs.py — read one run log and print what each claim did, in order.

    python dump_runs.py                                   # every arm's summary
    python dump_runs.py week7/agent_runs.jsonl c08         # one claim, full trace
    python dump_runs.py week7/agent_defended_runs.jsonl   # the defended arm

`week7_race.py` prints a scoreboard; this prints the evidence behind it. Every
per-claim table in `.docs/outputs/w*-walkthrough.md` was read off this, so the
prose and the JSONL cannot drift apart. Offline: no model, no network.

Where a run was quarantined by the D3 output guard, the summary line grades
`output_raw` — what the model actually wrote — and says so, because the
appended quarantine block would otherwise be scored as the model's verdict.
"""

import argparse
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "src"))

from claims import by_case, grade_output


def load(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", nargs="?", default="week7/agent_runs.jsonl")
    ap.add_argument("case_id", nargs="?", help="one claim, with every call and its output")
    ap.add_argument("--calls", action="store_true", help="print every call for every claim")
    args = ap.parse_args()

    rows = load(args.path)
    print("records:", len(rows))
    for r in rows:
        if args.case_id and r["case_id"] != args.case_id:
            continue
        raw = r.get("output_raw", r["output"])
        quarantined = bool(r.get("guard") and not r["guard"].get("ok", True))
        g = grade_output(raw, by_case(r["case_id"]))
        u = r["usage"]
        print("\n=== %s %s | %s $%s | laps=%s tok=%s $%s | stop=%s%s" % (
            r["case_id"], "PASS" if g["pass"] else "FAIL", g["got"]["status"],
            g["got"]["payable_usd"], u["laps"], u["total_tokens"], u["cost_usd"],
            r["stop_reason"], "  [quarantined by D3]" if quarantined else ""))
        print("  path: " + ">".join(r["trajectory"]))

        if args.calls or args.case_id:
            for c in r.get("calls", []):
                print("   -> %s %s" % (c["tool"],
                                       json.dumps(c["args"], ensure_ascii=False)[:220]))
                print("      ok=%s problems=%s rejected=%s"
                      % (c.get("ok"), c.get("arg_problems"), c.get("rejected_by")))
        if args.case_id:
            print("--- output ---")
            print(r["output"])


if __name__ == "__main__":
    main()
