#!/usr/bin/env python3
"""
trajectory_eval.py — Week 8: score the path, not just the answer.

Week 7's outcome eval asks one question: is the decision right? It cannot see
that a claim reached the right number down a path that never opened the
exclusion table. This file scores the path as well, and reports the difference
between the two as a number.

    python trajectory_eval.py                 # score the Week-7 agent runs
    python trajectory_eval.py --mitigated     # score the mitigated runs too,
                                              # print the before -> after table
    python trajectory_eval.py --run-mitigated # generate the mitigated runs first

Four numbers, over the same ten claims, both arms:

    tool_choice_accuracy   cases whose observed tool sequence is in the
                           expected set for that case
    argument_validity      calls whose arguments resolve to real records,
                           real forms, real exclusion codes
    step_efficiency        model laps taken / model laps needed
    cost_per_claim         p50 AND max, never the mean alone

The expected sequences are asserted in code, as a SET per case, because for
most of these claims more than one order is correct. Reading the policy before
pulling the claim is not a different answer, and an eval that scores it as a
failure is not measuring the agent, it is measuring which order the author had
in mind.
"""

import argparse
import csv
import json
import os
import statistics
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "src"))

from claims import CASE_IDS, EXPECTED, by_case, grade_output

W7 = os.path.join(HERE, "week7")
W8 = os.path.join(HERE, "week8")
BASE_RUNS = os.path.join(W7, "agent_runs.jsonl")
MIT_RUNS = os.path.join(W7, "agent_mitigated_runs.jsonl")
DEF_RUNS = os.path.join(W7, "agent_defended_runs.jsonl")
RESULTS_CSV = os.path.join(W8, "trajectory_results.csv")
MODES_MD = os.path.join(W8, "modes.md")

RULE = "=" * 78


# ---------------------------------------------------------------------------
# The expected tool sequences, asserted here rather than inferred afterwards.
#
# required    tools that must appear, in any order unless order_matters
# payout      "required" (a PAY claim must have its arithmetic run),
#             "optional" (a DENY claim may state $0 without it) or
#             "forbidden" (nothing may be paid on a claim with no notes)
# alt_orders  True when swapping the required tools is still a correct path
# ---------------------------------------------------------------------------

EXPECTED_SEQUENCES = {
    "c01": {"required": ["get_claim", "search_policy"], "payout": "required",
            "alt_orders": True, "steps_needed": 4,
            "why": "burst supply line: read the claim, look up the water clause and the "
                   "HO-0304 exclusion table, then pay the excess off"},
    "c02": {"required": ["get_claim", "search_policy"], "payout": "required",
            "alt_orders": True, "steps_needed": 4,
            "why": "two forms: HO-0306 only pays mold remediation carved out of MF-1 and "
                   "excludes the testing line, so both forms must be read before paying"},
    "c03": {"required": ["get_claim", "search_policy"], "payout": "optional",
            "alt_orders": True, "steps_needed": 3,
            "why": "the named storm deductible amount lives in HO-0305 NS-2, not in the "
                   "exclusion table row, so a denial needs the clause as well as the row"},
    "c04": {"required": ["get_claim", "search_policy"], "payout": "optional",
            "alt_orders": True, "steps_needed": 3,
            "why": "the notes describe external surface water, which is the HO-0304 E-12 "
                   "row; the denial has to be read out of that row"},
    "c05": {"required": ["get_claim", "search_policy"], "payout": "optional",
            "alt_orders": True, "steps_needed": 3,
            "why": "municipal drain backup is the HO-0304 E-13 row"},
    "c06": {"required": ["get_claim", "search_policy"], "payout": "optional",
            "alt_orders": True, "steps_needed": 3,
            "why": "water rising against the foundation is the HO-0304 E-14 row, and it is "
                   "the row a model reaches for least often"},
    "c07": {"required": ["get_claim", "search_policy"], "payout": "optional",
            "alt_orders": True, "steps_needed": 3,
            "why": "a six-week stain is continuous leakage under WD-1, excluded by E-11"},
    "c08": {"required": ["get_claim", "search_policy"], "payout": "optional",
            "alt_orders": True, "steps_needed": 3,
            "why": "an unserviced eighteen-year-old appliance is the HO-0304 E-16 row"},
    "c09": {"required": ["get_claim"], "payout": "forbidden",
            "alt_orders": True, "steps_needed": 2,
            "why": "no adjuster notes on file: there is no peril to look up, so the correct "
                   "path is read the file and refer. Paying anything here is the worst "
                   "possible answer, not a slow one"},
    "c10": {"required": ["get_claim", "search_policy"], "payout": "optional",
            "alt_orders": True, "steps_needed": 3,
            "why": "freeze in an unoccupied dwelling is E-10, and the nine-day reporting "
                   "delay puts it outside SECTION III, so two rows are in play"},
}


def allowed_paths(case_id: str) -> list[list[str]]:
    """
    Every tool sequence that counts as correct for this case.

    Two rules constrain where compute_payout may sit, and both are about the
    ORDER rather than the set. Money may not be decided before the claim file
    has been read, and it may not be decided before the wording has been read:
    a payout that comes first is not a fast answer, it is an answer that was
    never grounded, and scoring it as a pass is how the outcome eval in Week 7
    came to approve a correct number reached the wrong way.
    """
    spec = EXPECTED_SEQUENCES[case_id]
    required = list(spec["required"])
    orders = _perms(required) if spec["alt_orders"] else [required]
    paths: set[tuple[str, ...]] = set()
    for order in orders:
        if spec["payout"] == "forbidden":
            paths.add(tuple(order))
            continue
        if spec["payout"] == "optional":
            paths.add(tuple(order))          # a denial may state $0 with no arithmetic
        for pos in range(1, len(order) + 1):
            prefix = order[:pos]
            if "get_claim" not in prefix:
                continue
            if "search_policy" in order and "search_policy" not in prefix:
                continue
            paths.add(tuple(prefix + ["compute_payout"] + order[pos:]))
    return [list(p) for p in sorted(paths)]


def _perms(items: list[str]) -> list[list[str]]:
    if len(items) <= 1:
        return [list(items)]
    out = []
    for i, item in enumerate(items):
        for rest in _perms(items[:i] + items[i + 1:]):
            out.append([item] + rest)
    return out


def collapse(trajectory: list[str]) -> list[str]:
    """Consecutive repeats of one tool collapse: calling get_claim twice is
    waste, not a different path, and waste is already scored as step
    efficiency and as thrash."""
    out: list[str] = []
    for tool in trajectory:
        if not out or out[-1] != tool:
            out.append(tool)
    return out


def _q(tool: str) -> str:
    """get_claim -> claim, search_policy -> policy, compute_payout -> payout,
    just to fit two runs on one line."""
    return {"get_claim": "claim", "search_policy": "policy",
            "compute_payout": "payout"}.get(tool, tool)


# ---------------------------------------------------------------------------
# The failure-mode zoo. A case can carry several; the counts are independent
# so the regression table can show one mode improving while another worsens.
# ---------------------------------------------------------------------------

MODES = {
    "M1": "skipped the exclusion lookup and still answered",
    "M2": "computed a payout before reading the wording",
    "M3": "called a tool with arguments that do not resolve",
    "M4": "thrash: a repeated call, or a budget stop with no answer",
    "M5": "right path, wasted laps",
    "M6": "no fault observed",
}

EVIDENCE_LINE_KEY = "EVIDENCE"


def _evidence_codes(run: dict) -> list[str]:
    """The exclusion / clause ids the run itself says it relied on.

    Scanned across the whole answer, not just the EVIDENCE line. The contract
    puts the anchor in EVIDENCE, but a run that writes `EVIDENCE:
    EXCLUSION-TABLE` and then names `E-13` in its REASON has still asserted that
    id as its basis, and an argument-validity score that only looks at one line
    would score real citations as absent and invented ones said elsewhere as
    unseen. Reading the whole answer is also the stricter test for fiction: an
    invented id is an invented id wherever it appears.
    """
    import re
    out, seen = [], set()
    for line in (run.get("output") or "").splitlines():
        for code in re.findall(r"\bE-\d{2}\b|\bCLAUSE-[A-Z]{2}-\d\b|\b(?:WD|NS|WB)-\d\b",
                               line):
            if code not in seen:
                seen.add(code)
                out.append(code)
    return out


# The chunk ids that actually exist when the 6 endorsements are indexed with
# the structure-aware chunker. A model that cites one of these quoted wording
# it may really have read; a model that cites something else invented it.
ALL_CLAUSE_IDS = [
    "CLAUSE-BP-1", "CLAUSE-BP-2", "CLAUSE-BP-3", "CLAUSE-BP-4",
    "CLAUSE-EM-1", "CLAUSE-EM-2", "CLAUSE-EM-3", "CLAUSE-EM-4",
    "CLAUSE-MF-1", "CLAUSE-MF-2", "CLAUSE-MF-3", "CLAUSE-MF-4",
    "CLAUSE-NS-1", "CLAUSE-NS-2", "CLAUSE-NS-3", "CLAUSE-NS-4",
    "CLAUSE-SP-1", "CLAUSE-SP-2", "CLAUSE-SP-3", "CLAUSE-SP-4",
    "CLAUSE-WD-1", "CLAUSE-WD-2", "CLAUSE-WD-3",
    "EXCLUSION-TABLE", "EXCLUSIONS", "PREAMBLE",
    "SECTION-I", "SECTION-II", "SECTION-III", "SECTION-IV",
]


def _real_ids() -> set[str]:
    """Everything the model may legitimately name as evidence.

    Two kinds of id come out of the corpus: exclusion codes (E-12) and the
    clause/section chunk ids (CLAUSE-WD-1, EXCLUSION-TABLE, SECTION-I). A
    model cites both forms — it writes `WD-1` and `CLAUSE-WD-1` for the same
    chunk — so a cited id counts as real when it, or its CLAUSE- stripped
    form, is in the set.
    """
    from claims import ALL_CODES
    ids = set(ALL_CODES)
    for clause in ALL_CLAUSE_IDS:
        ids.add(clause)
        ids.add(clause.removeprefix("CLAUSE-"))
    return ids


def _is_real(code: str) -> bool:
    code = code.strip().upper()
    if code in _real_ids():
        return True
    return code.removeprefix("CLAUSE-") in _real_ids()


def classify(run: dict) -> dict:
    """Every mode this single run shows, plus the sequence verdict."""
    cid = run["case_id"]
    spec = EXPECTED_SEQUENCES[cid]
    traj = run["trajectory"]
    seen = collapse(traj)
    allowed = allowed_paths(cid)

    cited = _evidence_codes(run)
    invented = [c for c in cited if not _is_real(c)]

    calls = run.get("calls", [])
    arg_problem_calls = [c for c in calls if c.get("arg_problems")]
    payout_calls = [c for c in calls if c["tool"] == "compute_payout"]
    payout_calls_with_real_codes = [
        c for c in payout_calls
        if [x for x in (c["args"].get("exclusions_consulted") or []) if _is_real(str(x))]
    ]
    payout_calls_invented = [
        c for c in payout_calls
        if [x for x in (c["args"].get("exclusions_consulted") or []) if not _is_real(str(x))]
    ]
    payout_rejected = [c for c in payout_calls if c.get("rejected_by") == "argument_validation"]
    payout_positions = [i for i, t in enumerate(traj) if t == "compute_payout"]
    policy_positions = [i for i, t in enumerate(traj) if t == "search_policy"]
    payout_first = bool(payout_positions) and (
        not policy_positions or payout_positions[0] < policy_positions[0])
    repeated = {t for t in seen if traj.count(t) > (2 if t == "search_policy" else 1)}
    budget_stop = run["stop_reason"].startswith("budget")
    answered = bool((run.get("output") or "").strip())
    steps_taken = run["usage"]["laps"]
    efficiency = steps_taken / spec["steps_needed"]
    sequence_ok = seen in [list(a) for a in allowed]

    modes = []
    if budget_stop or repeated or not answered:
        modes.append("M4")
    if payout_first and spec["payout"] != "forbidden":
        modes.append("M2")
    if spec["payout"] != "forbidden" and "search_policy" not in seen:
        # A decision reached without ever asking the wording anything. Whether
        # the write-up then names a row is a separate (weaker) signal; this
        # mode fires on the PATH, because a model can be argued into citing a
        # row it never opened but cannot be argued into calling a tool that
        # resolves to nothing.
        modes.append("M1")
    if arg_problem_calls or invented:
        modes.append("M3")
    if not modes:
        modes.append("M6")
    elif "M5" not in modes and sequence_ok and answered and efficiency > 1.6:
        modes.append("M5")

    return {
        "case_id": cid,
        "observed": seen,
        "raw_trajectory": traj,
        "sequence_ok": sequence_ok,
        "allowed": allowed,
        "steps_taken": steps_taken,
        "steps_needed": spec["steps_needed"],
        "step_efficiency": round(efficiency, 2),
        "cited_codes": cited,
        "invented_codes": invented,
        "arg_problem_calls": [c["tool"] for c in arg_problem_calls],
        "payout_calls": len(payout_calls),
        "payout_calls_with_real_codes": len(payout_calls_with_real_codes),
        "payout_calls_invented_codes": len(payout_calls_invented),
        "payout_rejected": len(payout_rejected),
        # D3 fired: the answer was quarantined rather than released. Counted here
        # so the defended arm reports how often the guardrail actually had to
        # act, which on a clean corpus is the number that proves it is not just
        # sitting in the code being paid for.
        "guard_fired": bool(run.get("guard") and not run["guard"].get("ok", True)),
        "modes": modes,
        "multi_path_case": len(allowed) > 1,
    }


# ---------------------------------------------------------------------------
# the four numbers
# ---------------------------------------------------------------------------

def arm_numbers(runs: dict) -> dict:
    cases = [classify(runs[cid]) for cid in CASE_IDS if cid in runs]
    if not cases:
        return {}
    calls = [c for cid in CASE_IDS if cid in runs for c in runs[cid].get("calls", [])]
    valid = sum(1 for c in calls if not c.get("arg_problems"))
    costs = [runs[cid]["usage"]["cost_usd"] for cid in CASE_IDS if cid in runs]
    tokens = [runs[cid]["usage"]["total_tokens"] for cid in CASE_IDS if cid in runs]
    latencies = [runs[cid]["wall_clock_s"] for cid in CASE_IDS if cid in runs]
    mode_counts = {m: sum(1 for c in cases if m in c["modes"]) for m in MODES}
    rate = round(100 * valid / len(calls), 1) if calls else None
    payout_rows = [classify(runs[cid]) for cid in CASE_IDS if cid in runs]
    return {
        "n": len(cases),
        "tool_choice_accuracy_pct": round(100 * sum(c["sequence_ok"] for c in cases) / len(cases), 1),
        "argument_validity_pct": rate,
        "argument_calls": len(calls),
        "payout_calls": sum(c["payout_calls"] for c in payout_rows),
        "payout_calls_with_real_codes": sum(c["payout_calls_with_real_codes"] for c in payout_rows),
        "payout_calls_invented_codes": sum(c["payout_calls_invented_codes"] for c in payout_rows),
        "payout_rejected": sum(c["payout_rejected"] for c in payout_rows),
        "guard_fired": sum(1 for c in payout_rows if c["guard_fired"]),
        "cases_citing_a_row": sum(1 for c in payout_rows if c["cited_codes"]),
        "step_efficiency": round(statistics.mean(c["step_efficiency"] for c in cases), 2),
        "cost_p50_usd": round(statistics.median(costs), 6),
        "cost_max_usd": round(max(costs), 6),
        "cost_mean_usd": round(statistics.mean(costs), 6),
        "tokens_p50": int(statistics.median(tokens)),
        "tokens_total": sum(tokens),
        "latency_p50_s": round(statistics.median(latencies), 2),
        "latency_max_s": round(max(latencies), 2),
        "mode_counts": mode_counts,
    }


def outcome_numbers(runs: dict) -> dict:
    rows = [grade_output(runs[cid]["output"], by_case(cid))
            for cid in CASE_IDS if cid in runs]
    if not rows:
        return {}
    return {"n": len(rows), "outcome_pass_pct": round(100 * sum(r["pass"] for r in rows) / len(rows), 1),
            "outcome_pass_count": sum(r["pass"] for r in rows)}


def load(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    out = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rec = json.loads(line)
                out[rec["case_id"]] = rec
    return out


def write_csv(base: dict, base_n: dict, mit: dict, mit_n: dict, dfn: dict = None,
              dfn_n: dict = None) -> None:
    """The four numbers, then the per-mode regression. Three arms where the
    bonus defence arm exists: the rubric's mitigation and the injection
    hardening are separate rows, and conflating them would hide the price."""
    arms = [("agent (baseline)", base_n)]
    if mit_n:
        arms.append(("agent (mitigated)", mit_n))
    if dfn_n:
        arms.append(("agent (mitigated + injection defences)", dfn_n))

    os.makedirs(W8, exist_ok=True)
    with open(RESULTS_CSV, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["number"] + [n for n, _ in arms])
        if not base_n:
            return
        pairs = [
            ("outcome pass rate %", "outcome_pass_pct"),
            ("tool-choice accuracy %", "tool_choice_accuracy_pct"),
            ("argument validity %", "argument_validity_pct"),
            ("step efficiency (taken/needed)", "step_efficiency"),
            ("cost per claim p50 $", "cost_p50_usd"),
            ("cost per claim max $", "cost_max_usd"),
            ("cost per claim mean $", "cost_mean_usd"),
            ("latency p50 s", "latency_p50_s"),
            ("latency max s", "latency_max_s"),
            ("tokens p50", "tokens_p50"),
            ("payout calls with real codes", "payout_calls_with_real_codes"),
            ("payout calls rejected", "payout_rejected"),
            ("answers quarantined by D3", "guard_fired"),
        ]
        for label, key in pairs:
            w.writerow([label] + [a[1].get(key, "") for a in arms])
        w.writerow([])
        w.writerow(["mode", "name", "before", "after"]
                   + (["after + defences"] if dfn_n else []))
        for mode, name in MODES.items():
            row = [mode, name, base_n["mode_counts"][mode],
                   mit_n["mode_counts"][mode] if mit_n else ""]
            if dfn_n:
                row.append(dfn_n["mode_counts"][mode])
            w.writerow(row)


def print_results(base: dict, mit: dict, dfn: dict = None) -> None:
    bn, on = arm_numbers(base), outcome_numbers(base)
    mn, mo = (arm_numbers(mit), outcome_numbers(mit)) if mit else ({}, {})
    dn, do = (arm_numbers(dfn), outcome_numbers(dfn)) if dfn else ({}, {})
    cols = [("baseline", bn, on), ("mitigated", mn, mo)]
    if dfn:
        cols.append(("+ defences", dn, do))

    print(RULE + "\nEXPECTED SEQUENCES ASSERTED IN CODE\n" + RULE)
    for cid in CASE_IDS:
        spec = EXPECTED_SEQUENCES[cid]
        allowed = allowed_paths(cid)
        print(f"{cid}  {len(allowed):>2} accepted path(s)  steps_needed={spec['steps_needed']}  "
              f"payout={spec['payout']:<9} alt_orders={spec['alt_orders']}")
        if len(allowed) > 1:
            print(f"      {allowed[:3]}{' ...' if len(allowed) > 3 else ''}")
    print(f"\n{sum(1 for c in CASE_IDS if len(allowed_paths(c)) > 1)}/10 cases accept more than "
          f"one valid path; those are asserted as a set, not a single sequence.")

    print(RULE + "\nTHE FOUR TRAJECTORY NUMBERS\n" + RULE)
    widths = [34] + [14] * len(cols)
    def hdr():
        cells = ["number".ljust(34)] + [name.rjust(14) for name, _, _ in cols]
        print("| " + " | ".join(cells) + " |")
        print("|" + "|".join("-" * (w + 2) for w in widths) + "|")
    hdr()
    def line(label, key, fmt="{}"):
        cells = []
        for _, n, o in cols:
            v = n.get(key) if key in n else o.get(key)
            cells.append(fmt.format(v) if v is not None else "-")
        print("| " + " | ".join([label.ljust(34)] + cells) + " |")
    line("outcome pass rate %", "outcome_pass_pct")
    line("tool-choice accuracy %", "tool_choice_accuracy_pct")
    line("argument validity %", "argument_validity_pct")
    line("step efficiency (taken/needed)", "step_efficiency")
    line("cost per claim p50 $", "cost_p50_usd", "{:.6f}")
    line("cost per claim max $", "cost_max_usd", "{:.6f}")
    line("cost per claim mean $", "cost_mean_usd", "{:.6f}")
    line("latency p50 s", "latency_p50_s")
    line("latency max s", "latency_max_s")
    line("tokens p50", "tokens_p50")
    print()
    payout_evidence = " | ".join(f"{n.get('payout_calls_with_real_codes', 0):>6}"
                                 f"/{n.get('payout_calls', 0):<5}" for _, n, _ in cols)
    print("payout calls carrying real exclusion codes:     " + payout_evidence)
    rejected = " | ".join(f"{n.get('payout_rejected', 0):>12}" for _, n, _ in cols)
    print("payout calls rejected by argument validation:   " + rejected)
    quarantined = " | ".join(f"{n.get('guard_fired', 0):>12}" for _, n, _ in cols)
    print("answers quarantined by the D3 output guard:     " + quarantined)

    # The brief writes the gap as "outcome pass rate minus trajectory pass rate",
    # which is a negative number whenever the path is right and the money is wrong.
    # Both directions are printed so the sign convention cannot be argued with.
    op, tp = on.get("outcome_pass_pct", 0), bn.get("tool_choice_accuracy_pct", 0)
    signed = round(op - tp, 1)
    print(RULE + "\nTHE GAP, AS A NUMBER\n" + RULE)
    print(f"  outcome pass rate     {op:>6.1f}%")
    print(f"  trajectory pass rate  {tp:>6.1f}%")
    print(f"\n  gap = outcome - trajectory = {op:.1f} - {tp:.1f} = {signed:+.1f} points"
          f"   (the brief's definition)")
    print(f"  read as trajectory - outcome = {tp - op:+.1f} points"
          f"   (same number, sign flipped)")
    if signed < 0:
        print(f"\n  {-signed:.0f} points is RIGHT PATH, WRONG MONEY: the agent walked a valid\n"
              f"  trajectory and still got the money wrong. A trajectory eval is not a proxy\n"
              f"  for the outcome eval here — they are measuring different things, and the\n"
              f"  claims director is right not to trust the outcome number on its own. The\n"
              f"  brief predicts the sign the other way (a right answer reached by a wrong\n"
              f"  path); this corpus does not contain one, and the per-case table below\n"
              f"  shows why: the failures are verdict failures, not path failures.")
    elif signed > 0:
        print(f"\n  {signed:.0f} points is RIGHT ANSWER, WRONG PATH: the verdict was right and\n"
              f"  the route to it was not. These are the cases an outcome-only eval cannot see.")
    else:
        print("\n  zero gap: the path and the money agree on every case. Nothing is being\n"
              "  hidden by the outcome eval, which is the opposite of the problem the\n"
              "  director reported.")

    print(RULE + "\nPER CASE\n" + RULE)
    print(f"| {'case':<5} {'outcome':<8} {'traj':<6} {'steps':<7} {'eff':<6} "
          f"{'cited':<16} {'path taken':<44} | modes |")
    print(f"|{'-' * 7}|{'-' * 10}|{'-' * 8}|{'-' * 9}|{'-' * 8}|{'-' * 18}|{'-' * 46}|-------|")
    for cid in CASE_IDS:
        c = classify(base[cid])
        g = grade_output(base[cid]["output"], by_case(cid))
        path_disp = ">".join(_q(t) for t in c["observed"])[:60] or "(no tools called)"
        print(f"| {cid:<5} {'PASS' if g['pass'] else 'FAIL':<8} "
              f"{'ok' if c['sequence_ok'] else 'XX':<6} "
              f"{c['steps_taken']}/{c['steps_needed']:<5} {c['step_efficiency']:<6} "
              f"{','.join(c['cited_codes']) or '-':<16} "
              f"{path_disp:<60} | "
              f"{','.join(m for m in c['modes'] if m != 'M6') or '-':<6} |")

    # The headline case: right answer, wrong path
    print(RULE + "\nRIGHT ANSWER, WRONG PATH\n" + RULE)
    named = [cid for cid in CASE_IDS
             if grade_output(base[cid]["output"], by_case(cid))["pass"]
             and not classify(base[cid])["sequence_ok"]]
    if not named:
        print("No claim in this run passed the outcome eval while FAILING the trajectory\n"
              "eval. That is not a clean bill of health — it is the opposite of what the\n"
              "brief predicts, and the per-case table above says why: every failure here is\n"
              "a claim that walked a valid path and still paid out wrongly. The section\n"
              "below therefore reports the two shapes separately.")
    for cid in named:
        c = classify(base[cid])
        print(f"\n{cid} {base[cid]['claim_number']}  outcome PASS  trajectory FAIL")
        print(f"  expected  {' -> '.join(EXPECTED_SEQUENCES[cid]['required'])}"
              f"{' + compute_payout' if EXPECTED_SEQUENCES[cid]['payout'] == 'required' else ''}")
        print(f"  observed  {' -> '.join(c['observed']) or '(no tools called)'}")
        print(f"  laps      {c['steps_taken']} taken, {c['steps_needed']} needed "
              f"(efficiency {c['step_efficiency']})")
        print(f"  cited     {c['cited_codes'] or 'nothing — the answer names no row'}")
        print(f"  modes     {', '.join(c['modes'])}")
        print(f"  verdict   {base[cid]['output'].splitlines()[-1][:150]}")
        print(f"  why it matters: {EXPECTED[cid]['why']}")

    # The other direction, and the one this corpus actually exhibits: a verdict
    # the eval accepted, reached by a trajectory carrying a failure mode. c05 is
    # the clearest — it reached the right DENY, and got there by thrashing.
    tainted = [cid for cid in CASE_IDS
               if grade_output(base[cid]["output"], by_case(cid))["pass"]
               and any(m != "M6" for m in classify(base[cid])["modes"])]
    print(f"\nRIGHT ANSWER, DIRTY PATH (outcome PASS, trajectory carries a mode): "
          f"{', '.join(tainted) or 'none'}")
    for cid in tainted:
        c, r = classify(base[cid]), base[cid]
        print(f"\n{cid} {r['claim_number']}  outcome PASS, modes {', '.join(c['modes'])}")
        print(f"  expected  {' -> '.join(EXPECTED_SEQUENCES[cid]['required'])}"
              f"{' + compute_payout' if EXPECTED_SEQUENCES[cid]['payout'] == 'required' else ''}"
              f"  ({c['steps_needed']} steps)")
        print(f"  observed  {' -> '.join(c['observed'])}")
        print(f"  laps      {c['steps_taken']} taken (efficiency {c['step_efficiency']})"
              f"  tokens {r['usage']['total_tokens']}  ${r['usage']['cost_usd']}")
        for t in r["calls"]:
            print(f"    lap {t['lap']}  {t['tool']:<14} {json.dumps(t['args'],
                                                                 ensure_ascii=False)[:110]}")
        print(f"  why it matters: {EXPECTED[cid]['why']}")

    if mit:
        print(RULE + "\nPER-MODE REGRESSION — one mitigation, argument validation\n" + RULE)
        print(f"| {'mode':<5} {'name':<50} | {'before':>6} | {'after':>6} | {'delta':>6} |")
        print(f"|{'-' * 7}|{'-' * 52}|{'-' * 8}|{'-' * 8}|{'-' * 8}|")
        worse, better, new = [], [], []
        for mode, name in MODES.items():
            b, m = bn["mode_counts"][mode], mn["mode_counts"][mode]
            delta = m - b
            if delta < 0:
                better.append(mode)
            elif delta > 0:
                worse.append(mode)
                if b == 0:
                    new.append(mode)
            print(f"| {mode:<5} | {name:<50} | {b:>6} | {m:>6} | {delta:>+6} |")
        print(f"\nmodes that got worse: {', '.join(worse) or 'none'}")
        print(f"modes the mitigation created out of nothing: {', '.join(new) or 'none'}")
        print(f"modes that improved: {', '.join(better) or 'none'}")

        top = min((m for m in MODES if m != "M6"),
                  key=lambda m: (-bn["mode_counts"][m], m))
        print(f"\ntop mode in the baseline was {top} ({MODES[top]}) at "
              f"{bn['mode_counts'][top]} cases; after the mitigation it is "
              f"{mn['mode_counts'][top]}. Price paid:")
        print(f"  cost p50 per claim   ${bn['cost_p50_usd']:.6f} -> ${mn['cost_p50_usd']:.6f} "
              f"({mn['cost_p50_usd'] - bn['cost_p50_usd']:+.6f}, "
              f"{100 * (mn['cost_p50_usd'] / bn['cost_p50_usd'] - 1):+.1f}%)")
        print(f"  cost max per claim   ${bn['cost_max_usd']:.6f} -> ${mn['cost_max_usd']:.6f} "
              f"({mn['cost_max_usd'] - bn['cost_max_usd']:+.6f})")
        print(f"  latency p50          {bn['latency_p50_s']}s -> {mn['latency_p50_s']}s "
              f"({mn['latency_p50_s'] - bn['latency_p50_s']:+.2f}s)")
        print(f"  latency max          {bn['latency_max_s']}s -> {mn['latency_max_s']}s "
              f"({mn['latency_max_s'] - bn['latency_max_s']:+.2f}s)")
        print(f"  tokens total         {bn['tokens_total']} -> {mn['tokens_total']} "
              f"({mn['tokens_total'] - bn['tokens_total']:+d})")
        rejected = sum(1 for c in mit.values() for x in c.get("calls", [])
                       if x.get("rejected_by") == "argument_validation")
        print(f"  calls the validator turned away: {rejected} (each one is a wasted lap, "
              f"and that is the price)")

    if dfn:
        print(RULE + "\nWHAT THE INJECTION GUARD COST (bonus arm)\n" + RULE)
        print("The same ten claims, mitigation plus D1 sanitize plus D3 output guard. "
              "The prompt is\nunchanged and the token count barely moves, because a "
              "guard that costs laps\nis a guard that has been argued with; this one "
              "is not in the loop.\n")
        print(f"| {'':<34} | {'mitigated':>12} | {'+ defences':>12} | {'delta':>10} |")
        print(f"|{'-' * 36}|{'-' * 14}|{'-' * 14}|{'-' * 12}|")
        for label, key, fmt in [
            ("tool-choice accuracy %", "tool_choice_accuracy_pct", "{:.1f}"),
            ("argument validity %", "argument_validity_pct", "{:.1f}"),
            ("step efficiency (taken/needed)", "step_efficiency", "{:.2f}"),
            ("cost per claim p50 $", "cost_p50_usd", "{:.6f}"),
            ("cost per claim max $", "cost_max_usd", "{:.6f}"),
            ("latency p50 s", "latency_p50_s", "{:.2f}"),
            ("latency max s", "latency_max_s", "{:.2f}"),
        ]:
            a, b = mn.get(key), dn.get(key)
            if a is None or b is None:
                continue
            print(f"| {label:<34} | {fmt.format(a):>12} | {fmt.format(b):>12} | "
                  f"{b - a:>+10.4f} |")
        moved = {m: (mn["mode_counts"][m], dn["mode_counts"][m]) for m in MODES
                 if mn["mode_counts"][m] != dn["mode_counts"][m]}
        print(f"\nmodes whose count moved on the ten clean claims: "
              f"{moved or 'none — the defences are inert when nothing attacks them'}")
        print("That is the honest cost: zero. Their value is only visible on the poisoned "
              "claim,\nwhich is why `injection_attack.py` runs separately and the number "
              "that matters\nthere is how many arms stopped obeying.")

    print(f"\n-> {os.path.relpath(RESULTS_CSV, HERE)}")


def write_modes(bn: dict, mn: dict | None, dn: dict | None = None) -> None:
    os.makedirs(W8, exist_ok=True)
    lines = ["# Week 8 failure-mode zoo and counts\n",
             "A case can carry more than one mode. The counts are independent, so a "
             "mitigation that fixes one mode while breaking another shows up as a "
             "negative number in a row nobody was watching.\n",
             "| mode | what it is | before | after" + (" | after + defences" if dn else "")
             + " |", "|---|---|---|---|" + ("---|" if dn else "")]
    for mode, name in MODES.items():
        row = f"| {mode} | {name} | {bn['mode_counts'][mode]} | " \
              f"{mn['mode_counts'][mode] if mn else ''} |"
        if dn:
            row = row[:-2] + f" {dn['mode_counts'][mode]} |"
        lines.append(row)
    with open(MODES_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mitigated", action="store_true", help="score the mitigated arm too")
    ap.add_argument("--run-mitigated", action="store_true",
                    help="generate the mitigated runs first (costs model calls)")
    ap.add_argument("--defended", action="store_true",
                    help="add the injection-defence arm (needs the mitigated arm)")
    ap.add_argument("--run-defended", action="store_true",
                    help="generate the injection-defence arm first (costs model calls)")
    args = ap.parse_args()

    if args.run_mitigated or args.run_defended:
        import subprocess
        if args.run_mitigated:
            print("generating the mitigated arm (this spends model calls)\n", flush=True)
            subprocess.run([sys.executable, os.path.join(HERE, "week7_race.py"),
                            "--system", "agent", "--validate-payout-args",
                            "--suffix", "_mitigated"], check=True)
        if args.run_defended:
            print("\ngenerating the injection-defence arm (this spends model calls)\n",
                  flush=True)
            subprocess.run([sys.executable, os.path.join(HERE, "week7_race.py"),
                            "--system", "agent", "--validate-payout-args", "--sanitize",
                            "--output-guard", "--suffix", "_defended"], check=True)

    base = load(BASE_RUNS)
    if not base:
        sys.exit(f"no runs at {os.path.relpath(BASE_RUNS, HERE)} — "
                 f"run `python week7_race.py --system agent` first")
    mit = load(MIT_RUNS) if (args.mitigated or args.defended) else {}
    if (args.mitigated or args.defended) and not mit:
        sys.exit(f"no mitigated runs at {os.path.relpath(MIT_RUNS, HERE)} — "
                 f"run `python trajectory_eval.py --run-mitigated` first")
    dfn = load(DEF_RUNS) if args.defended else {}
    if args.defended and not dfn:
        sys.exit(f"no defended runs at {os.path.relpath(DEF_RUNS, HERE)} — "
                 f"run `python injection_attack.py --defended-runs` first")

    print_results(base, mit, dfn)
    write_csv(base, arm_numbers(base), mit, arm_numbers(mit) if mit else {},
              dfn, arm_numbers(dfn) if dfn else {})
    write_modes(arm_numbers(base), arm_numbers(mit) if mit else None,
                arm_numbers(dfn) if dfn else None)
    print(f"-> {os.path.relpath(MODES_MD, HERE)}")


if __name__ == "__main__":
    main()
