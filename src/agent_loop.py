"""
agent_loop.py — Week 7: the tool-calling agent, and the four budgets that stop it.

The loop is deliberately small: ask the model, run whatever tools it asked for,
put the results back, ask again. What is NOT small is the budget accounting,
because that is the deliverable.

Four budgets, all four checked, before AND after every lap:

    max_iterations   how many model laps may run at all
    max_tokens       the SUM of every lap's usage, not the last lap's
    max_cost_usd     the same sum, priced
    max_wall_clock_s how long the app's own work took, summed

Two of these are easy to fake and are therefore the interesting ones:

  * `max_tokens` must accumulate. The loop re-sends the entire message list on
    every lap, so lap 5 costs roughly 5x what lap 1 did. A budget that reads
    `response.usage.total_tokens` from the final call only will report a
    fraction of what actually left the account.
  * `max_cost_usd` is a second gate over the same sum, priced at a stated
    tariff. It exists to be a separate lever, and it is checked separately.

`max_wall_clock_s` is measured as ACCUMULATED WORK, not elapsed wall clock,
for the same reason `call_model` reports only its successful call's latency:
this app runs on a free tier that admits 8,000 tokens a minute, so elapsed time
is mostly the provider's queue and the wall-clock budget would fire on the
throttle rather than on anything the loop did. Summed model time plus summed
tool time is the loop's own cost, it is the number that grows when the loop
thrashes, and it is the same quantity the race reports as latency.

The honest limit of that claim is recorded in `BudgetLedger` and measured, not
guessed: a non-streaming response has no time-to-first-token, so a call the
provider queued is indistinguishable from a call that thought for the same
length of time. Laps over `QUEUE_SUSPECT_S` are flagged and subtracted into a
reported split so a reader can see how much of a fired clock was the provider
and how much was the loop.
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_tools import argument_problems, call_tool, schemas
from answerer import MODEL
from claims import CONTRACT
from tracing import call_model

# Notional tariff. Groq's free tier bills $0.00, which would make "cost per
# claim" a column of zeroes and hide the whole axis the race is measured on.
# Every currency figure in the Week-7 and Week-8 tables is this tariff applied
# to real, metered token counts; swap these two numbers and the tables move.
USD_PER_MTOK_PROMPT = 0.15
USD_PER_MTOK_COMPLETION = 0.60

AGENT_TEMPERATURE = 0.0
AGENT_MAX_TOKENS = 700          # gpt-oss spends part of the budget reasoning

DEFAULT_BUDGETS = {
    "max_iterations": 14,
    "max_tokens": 45_000,
    "max_cost_usd": 0.030,
    "max_wall_clock_s": 90.0,
}

# A single model call longer than this is treated as provider queueing rather
# than as work the loop did, and is reported separately. The shipped corpus tops
# out around 3s a call, so anything past 10s is the throttle, not the agent.
QUEUE_SUSPECT_S = 10.0

# The last lap is reserved for the answer. On the final permitted lap the tools
# are withheld, so the model has to commit to the contract instead of opening
# one more search. Without this, a model that thrashes burns every lap on tool
# calls and the budget reports `stop_reason=budget:max_iterations` with an empty
# output — a configuration artifact, not a finding. (The first baseline run hit
# this on c01 and c08, which is why the cap is 14 and not 8.)
RESERVED_FINAL_LAP = 1

# The answer lap is the one whose output must be complete enough to parse, and
# gpt-oss spends part of max_tokens on reasoning, so it gets a larger cap than a
# tool-calling lap does.
FINAL_MAX_TOKENS = 900

FINAL_LAP_NUDGE = (
    "That is your last look at the policy. No more tools are available to you. "
    "Commit to the answer now, in exactly this form and nothing else:\n\n" + CONTRACT
)


def _is_stray_tool_call(exc: Exception) -> bool:
    """Groq refuses the whole request when a tools-less call comes back with a
    tool call in it. That is a recoverable condition on the final lap, not a bug."""
    text = str(exc)
    return "Tool choice is none" in text or "tool_use_failed" in text

BUDGET_NAMES = ("max_iterations", "max_tokens", "max_cost_usd", "max_wall_clock_s")

SYSTEM_PROMPT = f"""You are triaging ONE insurance claim for a claims department.

You have three tools. They do not overlap, and neither does your judgement:
  get_claim       what was claimed, and what the adjuster wrote down
  search_policy   what the policy wording says about a peril
  compute_payout  arithmetic on an amount you have already decided is covered

WORK THE CLAIM IN THIS ORDER:
1. get_claim the claim number.
2. Work out the peril the notes describe, in a few words.
3. search_policy that peril against each form named on the claim. Read the
   exclusion table rows it returns and decide which row, if any, governs.
4. If the claim has no adjuster notes on file, you cannot state a peril.
   STATUS is REFER and you stop there.
5. compute_payout for anything payable. A denied claim pays $0.
6. Answer in exactly this form and nothing else:

{CONTRACT}

search_policy takes the peril IN WORDS, not a code. Searching for "E-12" or
"exclusion" returns the table row, but searching for the same row five
different ways does not: name the peril once, in a sentence, and read what
comes back. If the hits do not settle the peril, search the OTHER form on the
claim, or say the wording does not settle it in REASON. A guess costs a lap and
guessing repeatedly costs the answer.

A coverage decision you did not read out of the wording is not a decision, it
is a guess, and a guess that pays someone is a bad-faith exposure. When in
doubt, say so in REASON and pick DENY or REFER rather than inventing cover.
"""


def price(prompt_tokens: int, completion_tokens: int) -> float:
    """The notional tariff above, applied to metered tokens."""
    return (prompt_tokens * USD_PER_MTOK_PROMPT
            + completion_tokens * USD_PER_MTOK_COMPLETION) / 1_000_000


def _usage(usage) -> tuple[int, int]:
    if usage is None:
        return 0, 0
    return int(usage.prompt_tokens or 0), int(usage.completion_tokens or 0)


def _fmt(used: dict, budgets: dict) -> str:
    return ", ".join(f"{k} {used[k]:.4g}/{budgets[k]:.4g}" for k in BUDGET_NAMES)


class BudgetLedger:
    """
    One claim's spend, and the four reasons a lap may not start.

    `check()` is called before every lap and `record()` after it, so a budget
    can fire on the way in (a previous lap used too much) and on the way out
    (this lap did). Either way the loop stops and says which budget fired.

    `app_time_s` is accumulated work — model latency plus tool execution — not
    elapsed wall clock. See the module docstring for why.

    ONE HONEST LIMITATION, measured rather than asserted. `call_model` can drop
    its own retry sleeps, but it cannot tell a slow generation from a fast
    generation that sat in the provider's queue: a non-streaming response gives
    one round-trip number and no time-to-first-token, so a call the free tier
    held for 105 seconds is indistinguishable from a call that genuinely thought
    for 105 seconds. `app_time_s` therefore counts provider queueing as work.
    Rather than pretend otherwise, `record()` flags any lap more than
    `QUEUE_SUSPECT_S` long, keeps those durations in `queue_suspect_s`, and every
    report prints the split. On the shipped corpus this split is 0.0s, so the
    `max_wall_clock_s=90` default is measuring what it claims to; on a throttled
    provider it is not, and the number to look at is the split, not the total.
    Streaming with `stream_options={"include_usage": True}` would split TTFT from
    generation properly and is the named fix.
    """

    def __init__(self, budgets: dict):
        self.b = dict(budgets)
        missing = [k for k in BUDGET_NAMES if k not in self.b]
        if missing:
            raise ValueError(f"budgets missing {missing}")
        self.app_time_s = 0.0
        self.laps = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.stops: list[dict] = []
        self.queue_suspect_s = 0.0
        self.slow_laps: list[dict] = []

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens

    @property
    def cost_usd(self) -> float:
        return price(self.prompt_tokens, self.completion_tokens)

    @property
    def work_clock_s(self) -> float:
        """`app_time_s` with the provider-queue suspects taken back out."""
        return round(self.app_time_s - self.queue_suspect_s, 2)

    def used(self) -> dict:
        return {
            "max_iterations": self.laps,
            "max_tokens": self.total_tokens,
            "max_cost_usd": self.cost_usd,
            "max_wall_clock_s": self.app_time_s,
        }

    def check(self) -> str | None:
        """The first budget that is already spent, or None if the lap may run."""
        used = self.used()
        for name in BUDGET_NAMES:
            if used[name] >= self.b[name]:
                return name
        return None

    def record(self, prompt_tokens: int, completion_tokens: int, seconds: float) -> None:
        self.laps += 1
        self.prompt_tokens += prompt_tokens
        self.completion_tokens += completion_tokens
        self.app_time_s += seconds
        if seconds >= QUEUE_SUSPECT_S:
            self.queue_suspect_s += seconds
            self.slow_laps.append({"lap": self.laps, "seconds": round(seconds, 2),
                                   "prompt_tokens": prompt_tokens,
                                   "completion_tokens": completion_tokens})

    def stop(self, reason: str, detail: str) -> None:
        self.stops.append({"budget": reason, "detail": detail, "laps": self.laps,
                           "total_tokens": self.total_tokens,
                           "cost_usd": round(self.cost_usd, 6),
                           "app_time_s": round(self.app_time_s, 2),
                           "work_clock_s": self.work_clock_s,
                           "queue_suspect_s": round(self.queue_suspect_s, 2)})

    def snapshot(self) -> dict:
        return {"laps": self.laps, "prompt_tokens": self.prompt_tokens,
                "completion_tokens": self.completion_tokens,
                "total_tokens": self.total_tokens, "cost_usd": round(self.cost_usd, 6),
                "app_time_s": round(self.app_time_s, 2),
                "work_clock_s": self.work_clock_s,
                "queue_suspect_s": round(self.queue_suspect_s, 2),
                "slow_laps": self.slow_laps,
                "budgets": dict(self.b)}


def run_agent(
    claim: dict,
    budgets: dict | None = None,
    validate_payout_args: bool = False,
    sanitize: bool = False,
    output_guard: bool = False,
) -> dict:
    """
    Triage one claim. Returns the run record both evals score.

    The record is deliberately self-contained: every lap's tool name, its raw
    arguments, whether the arguments resolved, the per-lap token usage and the
    final text. Week 7's race reads four numbers off it; Week 8's trajectory
    eval reads the path.

    `validate_payout_args` is the Week-8 single mitigation. `sanitize` and
    `output_guard` are the Week-8 bonus defences and are off unless asked for,
    so every reported number comes from a run with its switches stated.

    The `claim` passed in IS the record `get_claim` serves, so the text the model
    reads and the record the grader scores can never be two different files.
    """
    budgets = dict(DEFAULT_BUDGETS if budgets is None else budgets)
    ledger = BudgetLedger(budgets)
    tools = schemas(validate_payout_args)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",
         "content": f"Triage claim {claim['claim_number']}."},
    ]

    laps: list[dict] = []
    calls: list[dict] = []            # the trajectory, flattened for the Week-8 eval
    output = ""
    stop_reason = "answered"

    while True:
        fired = ledger.check()
        if fired is not None:
            stop_reason = f"budget:{fired}"
            ledger.stop(fired, f"{fired} exhausted after {ledger.laps} lap(s): "
                               f"{_fmt(ledger.used(), budgets)}")
            break

        # Last permitted lap: the tools are still in the request but the
        # provider is told not to use them, which is the only way to GUARANTEE
        # a text answer. Withholding the schemas entirely just makes the model
        # reach for a tool that is not there and the request fails.
        final_lap = (ledger.laps + RESERVED_FINAL_LAP) >= budgets["max_iterations"]
        if final_lap:
            messages.append({"role": "user", "content": FINAL_LAP_NUDGE})
        try:
            response, latency_ms = call_model(
                messages, model=MODEL, temperature=AGENT_TEMPERATURE,
                max_tokens=FINAL_MAX_TOKENS if final_lap else AGENT_MAX_TOKENS,
                tools=tools, tool_choice="none" if final_lap else None,
            )
        except Exception as exc:                          # noqa: BLE001
            if not final_lap or not _is_stray_tool_call(exc):
                raise
            stop_reason = "budget:max_iterations (stray tool call on the final lap)"
            ledger.stop("max_iterations", f"stray tool call on the reserved final lap: "
                                          f"{_fmt(ledger.used(), budgets)}")
            break
        prompt_tokens, completion_tokens = _usage(response.usage)
        tool_started = time.monotonic()
        ledger.record(prompt_tokens, completion_tokens, latency_ms / 1000.0)
        message = response.choices[0].message
        messages.append({
            "role": "assistant",
            "content": message.content or "",
            **({"tool_calls": [tc.model_dump() for tc in message.tool_calls]}
               if message.tool_calls else {}),
        })

        lap = {"lap": ledger.laps, "latency_ms": latency_ms,
               "prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens,
               "total_tokens": prompt_tokens + completion_tokens,
               "cum_tokens": ledger.total_tokens, "cum_cost_usd": round(ledger.cost_usd, 6),
               "cumulative_prompt_tokens_at_lap": ledger.prompt_tokens,
               "final_lap": final_lap, "tool_calls": []}

        if not message.tool_calls:
            output = (message.content or "").strip()
            laps.append(lap)
            # A budget checked ONLY on the way in can never stop a run that
            # finishes inside its own last lap, which is exactly the case the
            # token and cost ceilings care about: the run answers, and the
            # ceiling it was set to enforce is reported as untouched. So the
            # ledger is re-read here too. `stop_reason` stays `answered` —
            # the handler did get a verdict — but the overage is recorded rather
            # than hidden.
            spent = ledger.check()
            if spent is not None:
                stop_reason = f"answered (over budget: {spent})"
                ledger.stop(spent, f"{spent} reached on lap {ledger.laps}, the same lap that "
                                   f"produced the answer: {_fmt(ledger.used(), budgets)}. "
                                   f"The verdict below is real and over budget.")
            elif final_lap:
                # The iteration ceiling did its job: the model spent its last
                # permitted lap committing to a verdict instead of opening
                # another search. That is a budget firing, not a coincidence.
                ledger.stop("max_iterations",
                            f"the reserved final lap was lap {ledger.laps} of "
                            f"{budgets['max_iterations']}; further searching was refused and "
                            f"this answer is the last the budget buys")
            break

        if final_lap:
            # Tools were withheld, so this should be unreachable. If a model
            # asks for one anyway there is no budget left to answer in, so stop
            # rather than start a lap the budget will not pay for.
            output = (message.content or "").strip()
            stop_reason = "budget:max_iterations (tool call on the reserved final lap)"
            laps.append(lap)
            break

        for tc in message.tool_calls:
            name = tc.function.name
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {"_unparseable": tc.function.arguments}
            result = call_tool(name, args, validate_payout_args=validate_payout_args,
                               sanitize=sanitize, claim_override=claim)
            row = {"lap": ledger.laps, "tool": name, "args": args,
                   "ok": bool(result.get("ok")),
                   "arg_problems": argument_problems(name, args),
                   "rejected_by": result.get("rejected_by")}
            calls.append(row)
            lap["tool_calls"].append({"tool": name, "args": args, "ok": row["ok"]})
            messages.append({"role": "tool", "tool_call_id": tc.id,
                             "content": json.dumps(result, ensure_ascii=False)[:6000]})
        ledger.app_time_s += time.monotonic() - tool_started
        laps.append(lap)

    guard = None
    output_raw = output
    if output_guard and output:
        from sanitize import guardrail_block, output_guard as _guard
        guard = _guard(output, claim, set())
        if not guard["ok"]:
            # D3 is not an advisory. A failing answer is quarantined in place —
            # the text stays in the record for the auditor, and a REFER/$0 block
            # is appended so nothing downstream can read the model's verdict as
            # payable. `output_raw` is what the model actually wrote, so the
            # report can say "wanted to pay" and "would have paid" separately.
            output = output + "\n\n" + guardrail_block(guard)
            stop_reason = "guardrail:" + guard["problems"][0].split()[0]

    return {
        "case_id": claim["case_id"],
        "claim_number": claim["claim_number"],
        "system": "agent",
        "validate_payout_args": validate_payout_args,
        "sanitize": sanitize,
        "output_guard": bool(output_guard),
        "guard": guard,
        "output": output,
        "output_raw": output_raw,
        "stop_reason": stop_reason,
        "trajectory": [c["tool"] for c in calls],
        "calls": calls,
        "laps": laps,
        "budget_stops": ledger.stops,
        "usage": ledger.snapshot(),
        "wall_clock_s": round(ledger.app_time_s, 3),
        "work_clock_s": ledger.work_clock_s,
        "queue_suspect_s": round(ledger.queue_suspect_s, 2),
        "model": {"name": MODEL, "temperature": AGENT_TEMPERATURE,
                  "max_tokens": AGENT_MAX_TOKENS},
        "tools": [s["function"]["name"] for s in tools],
    }
