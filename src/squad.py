"""
squad.py — Week 10: the claims squad, and the single agent it is raced against.

Both arms do the Week-6 task: adjuster notes in, the eight-heading claim
summary out (prompts.SUMMARY_PROMPT_VERSIONS["s1"]), graded afterwards by the
same five assertions and the same judge_v1. Same model, same temperature, same
`search_policy` tool, same budget ledger. The only variable is the shape:

    single   one tool loop: read the notes, search the wording, write the summary

    squad    orchestrator.plan        notes -> coverage questions (JSON, no tools)
             -> exclusions_worker     coverage questions -> findings (search_policy only)
             -> notes_worker          notes -> the fact headings (no tools)
             -> orchestrator.synthesise  the two worker reports -> the summary

Context strategy, stated because it decides the token bill: the exclusions
worker never sees the adjuster notes, only the questions and the deciding facts
the orchestrator wrote for it; the synthesis call never sees the notes or the
raw wording, only the two worker reports. Each worker gets the narrowest prompt
and the fewest tools that do its job — the exclusions worker has one tool, the
notes worker none — because that is the only place a squad could beat the
single agent.

Every model call is tagged with the hand-off that caused it, so the token bill
can be attributed to a named hand-off rather than to "multi-agent".

`fail_worker="exclusions"` is the Week-10 fault injection: the exclusions
worker answers HTTP 500 on every attempt. The orchestrator retries once and
then hands the failure to synthesis as a report. What synthesis writes next is
the thing being measured, so there is deliberately no special-case rule for it.
"""

import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_loop import DEFAULT_BUDGETS, BudgetLedger, _is_stray_tool_call, _usage
from agent_tools import TOOL_SCHEMAS, call_tool
from answerer import MODEL
from prompts import SUMMARY_PROMPT_VERSIONS
from redaction import redact
from tracing import call_model

TEMPERATURE = 0.0
MAX_TOKENS = 1600          # every call, both arms; gpt-oss spends part of it reasoning
MAX_LAPS = 8               # per tool loop, both arms; the last lap withholds tools
WORKER_RETRIES = 1         # the orchestrator's retry policy on a failed worker

SEARCH_TOOLS = [s for s in TOOL_SCHEMAS if s["function"]["name"] == "search_policy"]

_S1 = SUMMARY_PROMPT_VERSIONS["s1"]["system"]
_HEADINGS = _S1[_S1.index("Write the summary with exactly"):]

FINAL_NUDGE = ("That was your last search. No more tools are available. Write your "
               "answer now, in exactly the required form and nothing else.")


class WorkerHTTPError(RuntimeError):
    """A worker that answered with an HTTP error instead of a report."""

    def __init__(self, worker: str, status: int):
        self.worker, self.status = worker, status
        super().__init__(f"{worker} returned HTTP {status} Internal Server Error")


class BudgetStop(RuntimeError):
    pass


# ---------------------------------------------------------------------------
# The meter: one ledger per run, every call tagged with its hand-off
# ---------------------------------------------------------------------------

class Meter:
    def __init__(self, budgets: dict | None = None):
        self.ledger = BudgetLedger(dict(DEFAULT_BUDGETS if budgets is None else budgets))
        self.calls: list[dict] = []

    def call(self, handoff: str, messages: list[dict], tools=None, tool_choice=None):
        fired = self.ledger.check()
        if fired is not None:
            self.ledger.stop(fired, f"{fired} exhausted before {handoff}")
            raise BudgetStop(fired)
        response, latency_ms = call_model(messages, model=MODEL, temperature=TEMPERATURE,
                                          max_tokens=MAX_TOKENS, tools=tools,
                                          tool_choice=tool_choice)
        p, c = _usage(response.usage)
        self.ledger.record(p, c, latency_ms / 1000.0)
        self.calls.append({"handoff": handoff, "n": len(self.calls) + 1,
                           "prompt_tokens": p, "completion_tokens": c,
                           "total_tokens": p + c, "latency_s": round(latency_ms / 1000.0, 3),
                           "messages_in": len(messages),
                           "finish_reason": response.choices[0].finish_reason})
        return response

    def totals(self) -> dict:
        return self.ledger.snapshot()


def _tool_loop(meter: Meter, handoff: str, messages: list[dict]) -> tuple[str, list[dict], str]:
    """Ask, run search_policy, put results back, ask again. Shared by both arms."""
    tool_calls: list[dict] = []
    for lap in range(1, MAX_LAPS + 1):
        final = lap == MAX_LAPS
        if final:
            messages.append({"role": "user", "content": FINAL_NUDGE})
        try:
            response = meter.call(handoff, messages, tools=SEARCH_TOOLS,
                                  tool_choice="none" if final else None)
        except Exception as exc:                              # noqa: BLE001
            if final and _is_stray_tool_call(exc):
                return "", tool_calls, "stray tool call on the final lap"
            raise
        msg = response.choices[0].message
        messages.append({"role": "assistant", "content": msg.content or "",
                         **({"tool_calls": [tc.model_dump() for tc in msg.tool_calls]}
                            if msg.tool_calls else {})})
        if not msg.tool_calls:
            return (msg.content or "").strip(), tool_calls, "answered"
        started = time.monotonic()
        for tc in msg.tool_calls:
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {"_unparseable": tc.function.arguments}
            result = call_tool(tc.function.name, args)
            tool_calls.append({"handoff": handoff, "lap": lap, "tool": tc.function.name,
                               "args": args, "ok": bool(result.get("ok")),
                               "chunk_ids": [h["chunk_id"] for h in result.get("hits", [])]})
            messages.append({"role": "tool", "tool_call_id": tc.id,
                             "content": json.dumps(result, ensure_ascii=False)[:6000]})
        meter.ledger.app_time_s += time.monotonic() - started
    return "", tool_calls, "max_laps"


def _record(arm: str, case: dict, notes: str, output: str, meter: Meter,
            tool_calls: list[dict], stop_reason: str, **extra) -> dict:
    usage = meter.totals()
    return {
        "case_id": case["case_id"], "arm": arm, "claim_number": case["claim_number"],
        "notes_redacted": notes, "policy_forms": case["policy_forms"],
        "output": output, "stop_reason": stop_reason,
        "calls": meter.calls, "tool_calls": tool_calls,
        "usage": usage, "total_tokens": usage["total_tokens"], "cost_usd": usage["cost_usd"],
        "latency_s": usage["app_time_s"],
        "model": {"name": MODEL, "temperature": TEMPERATURE, "max_tokens": MAX_TOKENS},
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        **extra,
    }


def _input_block(case: dict, notes: str) -> str:
    return f"POLICY FORMS ON FILE: {', '.join(case['policy_forms'])}\n\nADJUSTER NOTES:\n{notes}"


# ---------------------------------------------------------------------------
# Arm 1 — the single agent
# ---------------------------------------------------------------------------

SINGLE_SYSTEM = _S1 + """
You have one tool, search_policy, and no context is pre-loaded: the wording you
cite must come from search_policy results. Before writing, search the peril the
notes describe against each policy form on file, read the exclusion rows that
come back, and decide which row, if any, governs. Cite only chunk ids that
search_policy returned to you.
"""


def run_single(case: dict, budgets: dict | None = None) -> dict:
    notes, _ = redact(case["notes"], keep=("claim_number",))
    meter = Meter(budgets)
    messages = [{"role": "system", "content": SINGLE_SYSTEM},
                {"role": "user", "content": _input_block(case, notes)
                 + "\n\nWrite the claim summary using the headed lines above."}]
    try:
        output, tool_calls, stop = _tool_loop(meter, "single.loop", messages)
    except BudgetStop as exc:
        output, tool_calls, stop = "", [], f"budget:{exc}"
    return _record("single", case, notes, output, meter, tool_calls, stop)


# ---------------------------------------------------------------------------
# Arm 2 — the squad
# ---------------------------------------------------------------------------

PLAN_SYSTEM = """You are the orchestrator of a claims squad. You do not decide coverage
and you do not write the summary yet. Read the adjuster notes and decompose the
claim into the coverage questions a coverage specialist must answer from the
policy wording.

For each distinct peril or claimed item, write one question, and copy into
"facts" every fact from the notes that could decide it (cause, timing, how the
water or damage got in, age or maintenance of anything that failed, occupancy,
amounts). The specialist will NOT see the notes, only what you write here.

Reply with JSON only, no prose:
{"coverage_questions": [{"peril": "<a few words>", "facts": "<deciding facts>",
  "forms": ["<form numbers on file to search>"]}]}
Use one to three questions."""

EXCLUSIONS_SYSTEM = """You are the coverage and exclusions worker in a claims squad. You
receive coverage questions with the deciding facts. You do not see the claim file.

For each question, search_policy the peril against each form listed, read the
exclusion table rows and clauses that come back, and decide what the wording says.
Do not use general knowledge of insurance. Cite only chunk ids search_policy
returned to you.

Reply with one line per question and nothing else:
FINDING <n>: <COVERED | EXCLUDED | COVERED SUBJECT TO <condition> | UNDETERMINED> - <one
sentence naming the deciding wording and its exclusion code if any> [SOURCE: chunk_id | form_number | clause_id]"""

NOTES_SYSTEM = """You are the adjuster-note summary worker in a claims squad. From the
adjuster notes ONLY, write exactly these headed lines and nothing else:
CLAIM NUMBER:
DATE OF LOSS:
POLICY FORMS:
LOSS SUMMARY: (two or three sentences)
DEDUCTIBLE:
OPEN ITEMS:
State facts only. Do not say whether anything is covered."""

SYNTH_SYSTEM = _S1 + """
You are the orchestrator of a claims squad, writing the final summary. Instead of
raw context you receive two worker reports: the notes worker's facts and the
exclusions worker's coverage findings. Take loss facts ONLY from the notes report
and coverage statements ONLY from the findings. Keep each finding's qualifier and
its [SOURCE: ...] tag exactly as the worker wrote them.
"""


def _parse_plan(text: str, forms: list[str]) -> tuple[list[dict], str | None]:
    m = re.search(r"\{.*\}", text or "", re.DOTALL)
    try:
        qs = json.loads(m.group(0))["coverage_questions"] if m else None
    except (json.JSONDecodeError, KeyError, TypeError):
        qs = None
    if not qs:
        return [{"peril": "the loss described", "facts": "(planner output unparseable)",
                 "forms": forms}], "plan unparseable; fell back to one generic question"
    for q in qs:
        q["forms"] = [f for f in q.get("forms") or forms if f in forms] or forms
    return qs, None


def _exclusions_task(questions: list[dict]) -> str:
    return "\n".join(f"QUESTION {i}: {q.get('peril')}\n  facts: {q.get('facts')}\n"
                     f"  forms to search: {', '.join(q['forms'])}"
                     for i, q in enumerate(questions, 1))


def run_squad(case: dict, budgets: dict | None = None, fail_worker: str | None = None) -> dict:
    notes, _ = redact(case["notes"], keep=("claim_number",))
    meter = Meter(budgets)
    tool_calls: list[dict] = []
    events: list[str] = []
    reports: dict[str, str] = {}
    plan_raw, questions = "", []
    try:
        # 1. orchestrator.plan
        plan_raw = (meter.call("orchestrator.plan", [
            {"role": "system", "content": PLAN_SYSTEM},
            {"role": "user", "content": _input_block(case, notes)},
        ]).choices[0].message.content or "").strip()
        questions, plan_problem = _parse_plan(plan_raw, case["policy_forms"])
        if plan_problem:
            events.append(plan_problem)

        # 2. orchestrator -> exclusions_worker, with the retry policy
        task = _exclusions_task(questions)
        for attempt in range(1, WORKER_RETRIES + 2):
            try:
                if fail_worker == "exclusions":
                    raise WorkerHTTPError("exclusions_worker", 500)
                text, calls, stop = _tool_loop(meter, "orchestrator->exclusions_worker", [
                    {"role": "system", "content": EXCLUSIONS_SYSTEM},
                    {"role": "user", "content": task}])
                tool_calls += calls
                reports["exclusions"] = text
                events.append(f"exclusions_worker attempt {attempt}: {stop}")
                break
            except WorkerHTTPError as exc:
                events.append(f"exclusions_worker attempt {attempt}: {exc}")
                if attempt == WORKER_RETRIES + 1:
                    reports["exclusions"] = (f"WORKER FAILED: {exc} on {attempt} attempts. "
                                             f"No findings were returned.")

        # 3. orchestrator -> notes_worker
        reports["notes"] = (meter.call("orchestrator->notes_worker", [
            {"role": "system", "content": NOTES_SYSTEM},
            {"role": "user", "content": "ADJUSTER NOTES:\n" + notes},
        ]).choices[0].message.content or "").strip()

        # 4. workers -> orchestrator.synthesise
        output = (meter.call("workers->orchestrator.synthesise", [
            {"role": "system", "content": SYNTH_SYSTEM},
            {"role": "user", "content":
                "NOTES WORKER REPORT:\n" + reports["notes"]
                + "\n\nEXCLUSIONS WORKER REPORT:\n" + reports["exclusions"]
                + "\n\nWrite the claim summary using the headed lines above."},
        ]).choices[0].message.content or "").strip()
        stop = "answered"
    except BudgetStop as exc:
        output, stop = "", f"budget:{exc}"

    # Critical path if the two workers ran concurrently (they are independent).
    by = {}
    for c in meter.calls:
        by[c["handoff"]] = by.get(c["handoff"], 0.0) + c["latency_s"]
    critical = (by.get("orchestrator.plan", 0) + by.get("workers->orchestrator.synthesise", 0)
                + max(by.get("orchestrator->exclusions_worker", 0),
                      by.get("orchestrator->notes_worker", 0)))
    return _record("squad" if not fail_worker else f"squad_fail_{fail_worker}", case, notes,
                   output, meter, tool_calls, stop, plan_raw=plan_raw,
                   coverage_questions=questions, worker_reports=reports, events=events,
                   fail_worker=fail_worker, critical_path_s=round(critical, 3))
