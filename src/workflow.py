"""
workflow.py — Week 7: the same triage, hard-coded.

This is the control. It reads the same three tools, calls the same model, is
graded by the same `claims.grade_output`, and has to produce the same
CONTRACT. What it does not have is a loop: the order of the steps is written
here, in Python, and the model is never asked what to do next. Three model
calls, hard-coded, and two `if`s:

    step 1  get_claim(claim_number)                             tool, always
    step 2  notes -> peril, forms, codes to look up             model call #1
            if the file held no notes -> REFER and STOP         <- branch 1
    step 3  search_policy(peril, form) per form                 tool, always
            if step 2 found codes to look up
    step 4  search_policy("exclusion table " + peril, form)     tool, branch 2
    step 5  wording + file -> STATUS, covered amount, codes     model call #2
    step 6  compute_payout(...)                                 tool, Python arithmetic
    step 7  the contract from the fixed evidence set            model call #3

The two `if`s are the whole argument of the week. "Does the path vary by
input?" is the question the race is built to answer, and this file is where the
variation is written down so it can be counted: each branch is a plain test on
a value the previous step returned, never on what the model felt like doing
next. There is no `while`, no `for` over model decisions, and no "should I
call another tool" question anywhere in this file.

Three model calls rather than one is deliberate. An earlier draft adjudicated
in step 2, before it had read the wording, and paid a $4,150 named-storm claim
that the HO-0305 deductible should have denied. Racing a crippled workflow
would have decided the race by construction, which is the mistake the task
warns about. A fixed workflow that reasons after retrieval is the honest
opponent.
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_loop import (AGENT_MAX_TOKENS, AGENT_TEMPERATURE, DEFAULT_BUDGETS,
                        price as _price)
from agent_tools import argument_problems, call_tool
from answerer import MODEL
from claims import CONTRACT, REAL_CODES
from tracing import call_model

# gpt-oss spends part of max_tokens on reasoning, so a writer capped at the
# agent's 700 tokens can stop mid-line (c02's first workflow run produced
# "CLAIM NUMBER: CLM-"). The write step is the only step whose output must be
# complete enough to parse, so it gets its own cap.
WRITE_MAX_TOKENS = 1400

ANALYSE_SYSTEM = """You are a claims triage analyst working from a claim file.

You have NOT read the policy wording yet. Your job is to name the peril in
words precise enough to find its clause, name the forms to look in, and name
the exclusion codes that could govern it.

Reply with exactly these five lines:

PERIL: <the mechanism of loss in a few words, e.g. 'burst interior supply line releasing water'>
FORMS: <form numbers, comma separated>
CHECK: <exclusion codes that could govern this peril, from the list you were given, or NONE>
LOOKUP: <a second thing the decision will turn on besides the peril, e.g. 'named storm deductible amount', or NONE>
NEEDS_EXCLUSION_CHECK: <YES if any code could govern it, NO if the peril is plainly not in the table>

If the claim file has no adjuster notes, PERIL is NONE and NEEDS_EXCLUSION_CHECK is NO."""

ADJUDICATE_SYSTEM = """You are a claims adjudicator. You are given a claim file and the \
policy wording that governs it.

Rule: a coverage position you did not read out of the wording is not a position, \
it is a guess. If the wording does not settle the question, say STATUS REFER.

Reply with exactly these four lines:

STATUS: <PAY | DENY | REFER>
COVERED_USD: <the amount of the claim covered BEFORE the excess, 0 for DENY or REFER>
CODES: <the exclusion or clause ids from the wording above that you actually relied on>
REASON: <one sentence>"""

WRITE_SYSTEM = f"""You are writing the triage line for a claims handler.

Use ONLY the evidence bundle you are given. Do not add a code that is not in it.
Reply with exactly this form and nothing else:

{CONTRACT}"""


def _usage(usage) -> tuple[int, int]:
    if usage is None:
        return 0, 0
    return int(usage.prompt_tokens or 0), int(usage.completion_tokens or 0)


def _model_call(system: str, user: str, max_tokens: int) -> tuple[str, int, int, float]:
    response, latency_ms = call_model(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        model=MODEL, temperature=AGENT_TEMPERATURE, max_tokens=max_tokens)
    prompt_tokens, completion_tokens = _usage(response.usage)
    return (response.choices[0].message.content or "").strip(), prompt_tokens, \
        completion_tokens, latency_ms


def _parse_labelled(text: str, fields: list[str]) -> dict:
    out: dict = {}
    for line in (text or "").splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        if key.strip().upper() in fields:
            out[key.strip().upper()] = value.strip()
    return out


def _money(value: str) -> float:
    digits = "".join(ch for ch in (value or "") if ch.isdigit() or ch == ".")
    try:
        return float(digits) if digits else 0.0
    except ValueError:
        return 0.0


def _exclusion_hit(result: dict) -> bool:
    """Did the retrieval actually bring back an exclusion table? Branch 2's fallback."""
    return any("EXCLUSION-TABLE" in (h.get("clause_id") or "")
               for h in result.get("hits", []))


def _dedupe(hits: list[dict]) -> list[dict]:
    """
    One copy of each chunk, exclusion tables first, capped at six.

    The four hard-coded queries overlap heavily, and re-sending the same table
    four times would inflate this arm's token bill without adding evidence.
    """
    seen, out = set(), []
    for h in sorted(hits, key=lambda h: "EXCLUSION-TABLE" not in (h.get("clause_id") or "")):
        if h["chunk_id"] in seen:
            continue
        seen.add(h["chunk_id"])
        out.append(h)
    return out[:6]


def run_workflow(claim: dict, budgets: dict | None = None,   # noqa: ARG001
                 validate_payout_args: bool = False) -> dict:
    """
    The identical task with the loop removed.

    `validate_payout_args` exists so the Week-8 arm comparison runs through the
    identical switch: the workflow is also the "replace the agent" mitigation,
    and it must be measurable under the same flag.
    """
    t0 = time.monotonic()
    ledger = {"prompt_tokens": 0, "completion_tokens": 0, "laps": 0, "app_time_s": 0.0}
    calls: list[dict] = []
    laps: list[dict] = []
    branch = {"no_notes": False, "exclusion_table": False}

    def record(name: str, args: dict, result: dict) -> None:
        calls.append({"lap": ledger["laps"] + 1, "tool": name, "args": args,
                      "ok": bool(result.get("ok")),
                      "arg_problems": argument_problems(name, args),
                      "rejected_by": result.get("rejected_by")})

    def model_step(name: str, system: str, user: str, max_tokens: int) -> str:
        text, p, c, ms = _model_call(system, user, max_tokens)
        ledger["laps"] += 1
        ledger["prompt_tokens"] += p
        ledger["completion_tokens"] += c
        ledger["app_time_s"] += ms / 1000.0
        laps.append({"lap": ledger["laps"], "latency_ms": ms, "prompt_tokens": p,
                     "completion_tokens": c, "total_tokens": p + c,
                     "cum_tokens": ledger["prompt_tokens"] + ledger["completion_tokens"],
                     "step": name})
        return text

    def finish(output: str, stop_reason: str) -> dict:
        return _record(claim, output, stop_reason, calls, laps, ledger, t0,
                       validate_payout_args, branch)

    # --- step 1: the claim file, unconditionally -------------------------
    args1 = {"claim_number": claim["claim_number"]}
    file = call_tool("get_claim", args1, validate_payout_args=validate_payout_args)
    record("get_claim", args1, file)
    if not file.get("ok"):
        return finish(
            f"CLAIM NUMBER: {claim['claim_number']}\nSTATUS: REFER\nPAYABLE: $0\n"
            f"EVIDENCE: none\nREASON: The claim file could not be read from the adjuster "
            f"system, so no peril is on the record.", "FILE_UNREADABLE")

    file_block = json.dumps({k: v for k, v in file.items() if k != "redaction_counts"},
                            ensure_ascii=False)
    in_scope = sorted({c for f in file["policy_forms"] for c in REAL_CODES.get(f, [])})

    # --- step 2: one model call, before any wording is in sight ---------
    analysis_text = model_step(
        "analyse notes", ANALYSE_SYSTEM,
        f"CLAIM FILE:\n{file_block}\n\nEXCLUSION CODES IN SCOPE FOR THESE FORMS:\n"
        f"{in_scope}", AGENT_MAX_TOKENS)
    a = _parse_labelled(analysis_text, ["PERIL", "FORMS", "CHECK", "LOOKUP",
                                        "NEEDS_EXCLUSION_CHECK"])
    peril = (a.get("PERIL") or "NONE").strip()
    forms = [f.strip().upper() for f in (a.get("FORMS") or "").split(",")
             if f.strip().upper() in file["policy_forms"]] or list(file["policy_forms"])
    check = [c.strip().upper() for c in (a.get("CHECK") or "").split(",")
             if c.strip() and c.strip().upper() != "NONE"]
    lookup = (a.get("LOOKUP") or "").strip()
    wants_table = (a.get("NEEDS_EXCLUSION_CHECK", "").upper() != "NO") or bool(check)

    # --- branch 1: no notes on file, no peril, hand to a human -----------
    if not file["notes_present"]:
        branch["no_notes"] = True
        return finish(
            f"CLAIM NUMBER: {claim['claim_number']}\nSTATUS: REFER\nPAYABLE: $0\n"
            f"EVIDENCE: none\nREASON: The claim file holds no adjuster notes, so no peril is "
            f"on the record and no coverage position can be stated; hand to a human adjuster.",
            "BRANCH_NO_NOTES")
    if peril.upper() in ("", "NONE"):
        # The notes are there but nothing in them names a peril. A different
        # failure from a missing file, and it must not borrow its wording.
        branch["no_peril"] = True
        return finish(
            f"CLAIM NUMBER: {claim['claim_number']}\nSTATUS: REFER\nPAYABLE: $0\n"
            f"EVIDENCE: none\nREASON: The adjuster notes do not name a peril, so there is "
            f"nothing for the wording to be checked against; hand to a human adjuster.",
            "BRANCH_NO_PERIL")

    # --- steps 3 and 4: the wording, and the branch on what step 2 found -
    evidence: list[dict] = []
    for form in forms:
        args = {"query": peril, "form_number": form}
        result = call_tool("search_policy", args, validate_payout_args=validate_payout_args)
        record("search_policy", args, result)
        evidence.extend(result.get("hits", []))
        if wants_table or _exclusion_hit(result):
            branch["exclusion_table"] = True
            args2 = {"query": f"exclusion table {peril}", "form_number": form}
            result2 = call_tool("search_policy", args2,
                                validate_payout_args=validate_payout_args)
            record("search_policy", args2, result2)
            evidence.extend(result2.get("hits", []))
        # The second thing step 2 said the decision would turn on. A fixed
        # workflow can only look for clauses it was told to name in advance;
        # the order is hard-coded, the query text is not.
        if lookup and lookup.upper() != "NONE":
            args3 = {"query": lookup, "form_number": form}
            result3 = call_tool("search_policy", args3,
                                validate_payout_args=validate_payout_args)
            record("search_policy", args3, result3)
            evidence.extend(result3.get("hits", []))

    # --- step 5: adjudicate, now that the wording is in front of it ------
    evidence = _dedupe(evidence)
    bundle = json.dumps({
        "claim": {k: file[k] for k in ("claim_number", "policy_forms", "date_of_loss",
                                      "amount_claimed_usd", "excess_usd")},
        "peril": peril,
        "wording": [{"form_number": h["form_number"], "clause_id": h["clause_id"],
                     "text": h["text"][:900]} for h in evidence[:5]],
    }, ensure_ascii=False)
    verdict_text = model_step("adjudicate", ADJUDICATE_SYSTEM, bundle, AGENT_MAX_TOKENS)
    v = _parse_labelled(verdict_text, ["STATUS", "COVERED_USD", "CODES", "REASON"])
    status = v.get("STATUS", "REFER").upper()
    status = status if status in ("PAY", "DENY", "REFER") else "REFER"
    covered = min(_money(v.get("COVERED_USD", "0")), file["amount_claimed_usd"])

    # --- step 6: arithmetic, in Python, once -----------------------------
    payout_args = {
        "claim_number": claim["claim_number"],
        "claim_status": ("partially_approved" if 0 < covered < file["amount_claimed_usd"]
                         else "approved" if covered >= file["amount_claimed_usd"] else "denied"),
        "covered_amount_usd": round(covered),
        "excess_usd": round(file["excess_usd"]) if status == "PAY" else 0,
    }
    if validate_payout_args:
        payout_args["exclusions_consulted"] = check or ["E-00"]
    payout = call_tool("compute_payout", payout_args, validate_payout_args=validate_payout_args)
    record("compute_payout", payout_args, payout)
    if status != "PAY":
        payout = {**payout, "payable_usd": 0, "arithmetic": "denied or referred; $0 payable"}

    # --- step 7: the contract, one model call, fixed evidence ------------
    write_bundle = json.dumps({
        "claim_number": file["claim_number"],
        "adjudication": {"status": status, "covered_usd": round(covered),
                         "codes": v.get("CODES", ""), "reason": v.get("REASON", "")},
        "arithmetic": payout,
        "codes_available": sorted({c for f in file["policy_forms"]
                                   for c in REAL_CODES.get(f, [])}),
    }, ensure_ascii=False)
    output = model_step("write contract", WRITE_SYSTEM, write_bundle, WRITE_MAX_TOKENS)
    return finish(output, "ANSWERED")


def _record(claim, output, stop_reason, calls, laps, ledger, t0,
            validate_payout_args, branch) -> dict:
    total = ledger["prompt_tokens"] + ledger["completion_tokens"]
    return {
        "case_id": claim["case_id"],
        "claim_number": claim["claim_number"],
        "system": "workflow",
        "validate_payout_args": validate_payout_args,
        "output": output,
        "stop_reason": stop_reason,
        "branch": branch,
        "trajectory": [c["tool"] for c in calls],
        "calls": calls,
        "laps": laps,
        "budget_stops": [],
        "usage": {"laps": len(laps), "prompt_tokens": ledger["prompt_tokens"],
                  "completion_tokens": ledger["completion_tokens"],
                  "total_tokens": total,
                  "cost_usd": round(_price(ledger["prompt_tokens"],
                                          ledger["completion_tokens"]), 6),
                  "app_time_s": round(ledger["app_time_s"], 2),
                  "budgets": dict(DEFAULT_BUDGETS)},
        "wall_clock_s": round(ledger["app_time_s"], 3),
        "model": {"name": MODEL, "temperature": AGENT_TEMPERATURE,
                  "max_tokens": AGENT_MAX_TOKENS},
        "tools": ["get_claim", "search_policy", "compute_payout"],
    }
