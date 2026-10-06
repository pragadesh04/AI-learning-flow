"""
agent_tools.py — Week 7: the three tools the agent may call, and the dispatcher.

The descriptions are the whole design constraint of this week, so they are
written as three sentences that each name exactly one job and each say what
they do NOT do. Overlap is what makes a model call the wrong tool, so the
non-claims are as load-bearing as the claims:

    get_claim       reads the claim file.  Not the wording. Not money.
    search_policy   reads the wording.      Not any claim. Not money.
    compute_payout  does the arithmetic.   Not the wording. Not the decision.

Week 7 rubric point 10 sits on the third tool: one job, an enum on
`claim_status`, and no wording shared with the first two. `TOOL_DESCRIPTIONS`
is diffed, with an overlap check, in `week7/tool_descriptions.md`.

`validate_payout_args` is the Week-8 single mitigation. It is OFF by default
and is the only thing that changes between the trajectory baseline and the
mitigated arm.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hybrid import fused_search
from redaction import redact
from sanitize import sanitize_untrusted

from claims import ALL_CODES, CLAIM_NUMBERS, FORMS, REAL_CODES, by_number

MAX_CHUNK_CHARS = 2000        # tool results are re-sent every lap; keep them small
N_RESULTS = 3

# The enum on compute_payout's claim_status parameter. Values are workflow
# states, not triage verdicts: the tool never decides PAY/DENY/REFER, it only
# takes the arithmetic the caller has already adjudicated.
CLAIM_STATUS_ENUM = [
    "open",
    "under_review",
    "partially_approved",
    "approved",
    "denied",
    "withdrawn",
]


# ---------------------------------------------------------------------------
# The schemas, as handed to the model
# ---------------------------------------------------------------------------

GET_CLAIM_DESC = (
    "Read the adjuster system and return the claim file filed under one claim "
    "number: date of loss, policy forms in force, amount claimed, the excess on "
    "file, and the adjuster's notes. This tool returns what was claimed. It "
    "does not return policy wording and it does not calculate anything."
)

SEARCH_POLICY_DESC = (
    "Search the indexed endorsement wording and return the clause text that "
    "governs a named peril, with its clause id and exclusion codes. This tool "
    "returns what the policy says. It does not know about any individual claim "
    "and it does not calculate anything."
)

COMPUTE_PAYOUT_DESC = (
    "Apply one policy excess to one already-adjudicated covered amount and "
    "return the payable figure with the arithmetic. This tool returns money "
    "only. It does not read policy wording and it does not decide whether a "
    "loss is covered."
)

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_claim",
            "description": GET_CLAIM_DESC,
            "parameters": {
                "type": "object",
                "properties": {
                    "claim_number": {
                        "type": "string",
                        "description": "The claim number exactly as filed, e.g. CLM-2024-31842.",
                    }
                },
                "required": ["claim_number"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_policy",
            "description": SEARCH_POLICY_DESC,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The peril in words, e.g. 'exclusion table flood surface water'.",
                    },
                    "form_number": {
                        "type": "string",
                        "enum": FORMS,
                        "description": "The endorsement form to search within.",
                    },
                },
                "required": ["query", "form_number"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compute_payout",
            "description": COMPUTE_PAYOUT_DESC,
            "parameters": {
                "type": "object",
                "properties": {
                    "claim_number": {
                        "type": "string",
                        "description": "The claim number this money belongs to.",
                    },
                    "claim_status": {
                        "type": "string",
                        "enum": CLAIM_STATUS_ENUM,
                        "description": "The claim's workflow state at the moment of payment.",
                    },
                    "covered_amount_usd": {
                        "type": "number",
                        "description": "The amount you have already adjudicated as covered.",
                    },
                    "excess_usd": {
                        "type": "number",
                        "description": "The policy excess to subtract. Use 0 if none applies.",
                    },
                },
                "required": ["claim_number", "claim_status", "covered_amount_usd", "excess_usd"],
            },
        },
    },
]

TOOL_DESCRIPTIONS = {
    s["function"]["name"]: s["function"]["description"] for s in TOOL_SCHEMAS
}

# Week 8, the single mitigation. When on, compute_payout also demands proof
# that the caller actually read the exclusions: a list of the exclusion codes
# it is relying on, checked against the codes that really exist in the corpus.
MITIGATED_PAYOUT_PARAMS = {
    "exclusions_consulted": {
        "type": "array",
        "items": {"type": "string"},
        "description": (
            "The exclusion codes from the wording you actually read before "
            "deciding, e.g. ['E-12']. May be empty only if the claim has no "
            "exclusion table in its forms."
        ),
    }
}


def schemas(validate_payout_args: bool = False) -> list[dict]:
    """The tool list as sent. The mitigation adds one parameter to one tool."""
    if not validate_payout_args:
        return TOOL_SCHEMAS
    out = json.loads(json.dumps(TOOL_SCHEMAS))
    payout = next(s for s in out if s["function"]["name"] == "compute_payout")
    payout["function"]["parameters"]["properties"].update(MITIGATED_PAYOUT_PARAMS)
    payout["function"]["parameters"]["required"].append("exclusions_consulted")
    return out


# ---------------------------------------------------------------------------
# Implementations
# ---------------------------------------------------------------------------

def tool_get_claim(args: dict, sanitize: bool = False,
                   claim_override: dict | None = None) -> dict:
    """
    The claim file. Notes are redacted on the way out, as every other path is.

    `claim_override` is the record the caller was asked to triage. It is passed
    in rather than re-fetched so that the text the model reads and the record the
    grader scores are the same object: a poisoned corpus must reach the model
    (Week 8's injection arm) and a patched corpus must not be able to be read
    from anywhere but here.
    """
    number = (args.get("claim_number") or "").strip()
    claim = (claim_override
             if claim_override is not None and claim_override["claim_number"] == number
             else by_number(number))
    if claim is None:
        return {"ok": False,
                "error": f"no claim file under {number!r}; the adjuster system has no such record",
                "known_claim_numbers": CLAIM_NUMBERS}
    notes, counts = redact(claim["adjuster_notes"], keep=("claim_number",))
    removed: list[dict] = []
    if sanitize:
        # Week 8 bonus, defence D1. The notes are untrusted text: they quote the
        # insured, who quotes a letter. Anything in them that reads as an
        # instruction is masked before the model ever sees it.
        notes, removed = sanitize_untrusted(notes)
    return {
        "ok": True,
        "claim_number": claim["claim_number"],
        "policy_forms": claim["policy_forms"],
        "coverage_a_limit_usd": claim["coverage_a_limit_usd"],
        "date_of_loss": claim["date_of_loss"],
        "amount_claimed_usd": claim["amount_claimed_usd"],
        "excess_usd": claim["excess_usd"],
        "notes_present": claim["notes_present"],
        "adjuster_notes": notes if claim["notes_present"] else
                          "NO ADJUSTER NOTES ON FILE FOR THIS CLAIM",
        "redaction_counts": counts,
        "sanitized_spans": len(removed),
    }


def tool_search_policy(args: dict) -> dict:
    """The endorsement wording that governs a peril, with real clause ids."""
    query = (args.get("query") or "").strip()
    form = (args.get("form_number") or "").strip().upper()
    if form not in FORMS:
        return {"ok": False, "error": f"unknown form {form!r}",
                "known_forms": FORMS}
    hits = fused_search(f"{query} {form}", strategy="structure_aware", n_results=N_RESULTS)
    return {
        "ok": True,
        "query": query,
        "form_number": form,
        "hits": [
            {
                "chunk_id": h["chunk_id"],
                "form_number": h["metadata"].get("form_number"),
                "clause_id": h["metadata"].get("clause_id"),
                "text": h["text"][:MAX_CHUNK_CHARS],
            }
            for h in hits if h["metadata"].get("form_number") == form
        ] or [
            {
                "chunk_id": h["chunk_id"],
                "form_number": h["metadata"].get("form_number"),
                "clause_id": h["metadata"].get("clause_id"),
                "text": h["text"][:MAX_CHUNK_CHARS],
            }
            for h in hits[:1]
        ],
    }


def tool_compute_payout(args: dict, validate_payout_args: bool = False) -> dict:
    """Arithmetic. Never a coverage decision."""
    claim = by_number((args.get("claim_number") or "").strip())
    covered = args.get("covered_amount_usd")
    excess = args.get("excess_usd", 0)

    if not isinstance(covered, (int, float)) or isinstance(covered, bool):
        return {"ok": False, "error": f"covered_amount_usd must be a number, got {covered!r}"}
    if not isinstance(excess, (int, float)) or isinstance(excess, bool):
        return {"ok": False, "error": f"excess_usd must be a number, got {excess!r}"}
    if claim is not None and covered > claim["amount_claimed_usd"]:
        return {"ok": False,
                "error": (f"covered_amount_usd {covered} is above the amount claimed "
                          f"({claim['amount_claimed_usd']}) on {claim['claim_number']}")}

    if validate_payout_args:
        codes = args.get("exclusions_consulted")
        if not isinstance(codes, list) or not codes:
            return {"ok": False, "rejected_by": "argument_validation",
                    "error": ("exclusions_consulted is required and must list the exclusion "
                              "codes you read before adjudicating. Call search_policy first, "
                              "then pass the codes back here.")}
        real = set(ALL_CODES)
        invented = [c for c in codes if str(c).upper() not in real]
        if invented:
            return {"ok": False, "rejected_by": "argument_validation",
                    "error": f"exclusion codes that do not exist in the corpus: {invented}",
                    "real_codes": ALL_CODES}

    payable = max(0, round(covered) - round(excess))
    out = {
        "ok": True,
        "claim_number": claim["claim_number"] if claim else args.get("claim_number"),
        "claim_status": args.get("claim_status"),
        "covered_amount_usd": round(covered),
        "excess_usd": round(excess),
        "payable_usd": payable,
        "arithmetic": f"{round(covered)} - {round(excess)} = {payable}",
    }
    if validate_payout_args:
        out["exclusions_accepted"] = [str(c).upper() for c in args["exclusions_consulted"]]
    return out


DISPATCH = {
    "get_claim": tool_get_claim,
    "search_policy": tool_search_policy,
}


def call_tool(name: str, args: dict, validate_payout_args: bool = False,
              sanitize: bool = False, claim_override: dict | None = None) -> dict:
    """Run one tool. An unknown name is an error result, never an exception:
    the model has to see it and recover, exactly as it would in production."""
    if name == "compute_payout":
        return tool_compute_payout(args, validate_payout_args=validate_payout_args)
    if name == "get_claim":
        return tool_get_claim(args, sanitize=sanitize, claim_override=claim_override)
    fn = DISPATCH.get(name)
    if fn is None:
        return {"ok": False, "error": f"no such tool: {name}"}
    try:
        return fn(args)
    except Exception as exc:                      # noqa: BLE001 - surfaced to the model
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


# ---------------------------------------------------------------------------
# Argument validity (Week 8). Pure, offline, and applied to a recorded call:
# were the claim numbers and exclusion clause ids real, or fluent fiction?
# ---------------------------------------------------------------------------

def argument_problems(name: str, args: dict) -> list[str]:
    problems: list[str] = []
    number = (args.get("claim_number") or "").strip()
    if name in ("get_claim", "compute_payout"):
        if number not in CLAIM_NUMBERS:
            problems.append(f"claim_number {number!r} is not a claim in the adjuster system")
    if name == "search_policy":
        form = (args.get("form_number") or "").strip().upper()
        if form not in FORMS:
            problems.append(f"form_number {form!r} is not an indexed form")
    if name == "compute_payout":
        status = args.get("claim_status")
        if status not in CLAIM_STATUS_ENUM:
            problems.append(f"claim_status {status!r} is not in the enum")
        for field in ("covered_amount_usd", "excess_usd"):
            v = args.get(field)
            if not isinstance(v, (int, float)) or isinstance(v, bool) or v < 0:
                problems.append(f"{field} {v!r} is not a non-negative number")
        codes = args.get("exclusions_consulted")
        if isinstance(codes, list):
            real = set(ALL_CODES)
            for c in codes:
                if str(c).upper() not in real:
                    problems.append(f"exclusion code {c!r} does not exist in the corpus")
    return problems


if __name__ == "__main__":
    for tool in TOOL_DESCRIPTIONS.values():
        print(tool, "\n")
    print("real codes:", ", ".join(ALL_CODES))
    print("arg problems on a plausible call:",
          argument_problems("compute_payout",
                            {"claim_number": "CLM-2024-31842", "claim_status": "paid",
                             "covered_amount_usd": "six thousand", "excess_usd": 1000,
                             "exclusions_consulted": ["E-19"]}))
    print("compute_payout with the mitigation on and no codes:",
          call_tool("compute_payout",
                    {"claim_number": "CLM-2024-31842", "claim_status": "approved",
                     "covered_amount_usd": 6200, "excess_usd": 1000},
                    validate_payout_args=True))
