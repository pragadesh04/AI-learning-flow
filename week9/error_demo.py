#!/usr/bin/env python3
"""
error_demo.py — Week 9: the same failing call, old error vs new error.

Left to itself, the v2 docstring stops the model from sending a bad form number
at all (week9/traces/error_v2.json), so a free run never shows the model
HANDLING the error. This replays the failure instead, holding everything but
the error text constant:

    1. every arm starts from the identical conversation: the system prompt, the
       question, and the model's own first call from the v1 run
       (search_policy form_number='HO-304')
    2. that call is sent to the REAL policy server, v1 or v2, and its real
       result is appended
    3. the model takes it from there, through the same loop

Only POLICY_SERVER_VERSION differs, so only the docstring and the error text
differ. The agent module is imported, not edited.

    python week9/error_demo.py        # -> week9/error_before_after.md
"""

import asyncio
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))

from dotenv import load_dotenv

load_dotenv(os.path.join(ROOT, ".env"))

from agent_loop import AGENT_TEMPERATURE
from answerer import MODEL
from mcp_agent import MAX_TOKENS, SYSTEM_PROMPT, Toolbox
from tracing import call_model

QUERY = ("Under form HO-304, which exclusion code governs flood from external surface "
         "water? Quote the code and the row.")
FAILING_CALL = {"form_number": "HO-304", "query": "flood external surface water exclusion"}
MAX_LAPS = 6
OUT = os.path.join(HERE, "error_before_after.md")


async def arm(version: str) -> dict:
    async with Toolbox(os.path.join(HERE, "configs", f"policy_v{version}.json")) as box:
        tools = box.schemas()
        seed = {"id": "call_seed", "type": "function",
                "function": {"name": "search_policy", "arguments": json.dumps(FAILING_CALL)}}
        _, is_error, text = await box.call("search_policy", FAILING_CALL)
        messages = [{"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": QUERY},
                    {"role": "assistant", "content": "", "tool_calls": [seed]},
                    {"role": "tool", "tool_call_id": "call_seed",
                     "content": json.dumps({"is_error": is_error, "content": text})}]
        steps = [{"call": FAILING_CALL, "is_error": is_error, "result": text, "seeded": True}]
        tokens, output = 0, ""
        for _ in range(MAX_LAPS):
            response, _ = call_model(messages, model=MODEL, temperature=AGENT_TEMPERATURE,
                                     max_tokens=MAX_TOKENS, tools=tools)
            tokens += response.usage.total_tokens if response.usage else 0
            msg = response.choices[0].message
            messages.append({"role": "assistant", "content": msg.content or "",
                             **({"tool_calls": [tc.model_dump() for tc in msg.tool_calls]}
                                if msg.tool_calls else {})})
            if not msg.tool_calls:
                output = (msg.content or "").strip()
                break
            for tc in msg.tool_calls:
                args = json.loads(tc.function.arguments or "{}")
                _, err, res = await box.call(tc.function.name, args)
                steps.append({"call": args, "is_error": err, "result": res, "seeded": False})
                messages.append({"role": "tool", "tool_call_id": tc.id,
                                 "content": json.dumps({"is_error": err, "content": res})})
        description = box.tools["search_policy"].description
    return {"version": version, "description": description, "steps": steps,
            "output": output, "tokens": tokens,
            "recovered": any(not s["is_error"] for s in steps)}


def _natural(version: str) -> dict:
    with open(os.path.join(HERE, "traces", f"error_v{version}.json"), encoding="utf-8") as fh:
        return json.load(fh)


def render(before: dict, after: dict) -> str:
    def transcript(a: dict) -> str:
        lines = []
        for i, s in enumerate(a["steps"], 1):
            tag = "seeded, identical in both arms" if s["seeded"] else "model's choice"
            lines.append(f"{i}. `search_policy {json.dumps(s['call'])}` ({tag})")
            lines.append(f"   - {'**isError**' if s['is_error'] else 'ok'}: "
                         f"`{s['result'][:220].replace(chr(10), ' ')}`")
        answer = (a["output"][:500].replace(chr(10), " ")
                  or f"(none: still calling tools when the {MAX_LAPS}-lap cap ran out)")
        lines.append(f"\n**Final answer:** {answer}")
        lines.append(f"\nRecovered: **{'yes' if a['recovered'] else 'no'}** · "
                     f"{len(a['steps'])} calls · {a['tokens']} tokens after the seed")
        return "\n".join(lines)

    nb, na = _natural("1"), _natural("2")
    return f"""# Same failing call: old docstring/error vs new

Tool: `search_policy` on OUR server (`mcp_servers/policy_server.py`). Only
`POLICY_SERVER_VERSION` differs (`week9/configs/policy_v1.json` vs `policy_v2.json`).
Question: *{QUERY}*

## Docstring as the model sees it (from tools/list)

**Before (v1):**
```
{before['description']}
```

**After (v2):**
```
{after['description']}
```

## Error text for the unknown-form path

- **Before:** the tool raised a bare `LookupError(3)`; the SDK hides crash text, so
  the model receives only `Error executing tool search_policy`. It cannot tell a bad
  argument from a dead server.
- **After:** a `ToolError` that says what is wrong and how to fix it:
  `{after['steps'][0]['result']}`

## Controlled replay: the same failing call, then the model takes over

### Before (v1)
{transcript(before)}

### After (v2)
{transcript(after)}

## Free runs, no replay (`week9/traces/error_v1.json`, `error_v2.json`)

| | failing calls | laps | tokens | answer |
|---|---|---|---|---|
| v1 | {sum(c['is_error'] for c in nb['calls'])} of {len(nb['calls'])} | {nb['usage']['laps']} | {nb['usage']['total_tokens']} | {nb['output'][:70]!r} |
| v2 | {sum(c['is_error'] for c in na['calls'])} of {len(na['calls'])} | {na['usage']['laps']} | {na['usage']['total_tokens']} | {na['output'][:70].replace(chr(10), ' ')!r} |

In the free run the v2 docstring ("four digits after 'HO-'") prevented the bad call
outright; the replay above is what shows the rewritten error being *handled*.
"""


def main() -> None:
    before = asyncio.run(arm("1"))
    after = asyncio.run(arm("2"))
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(render(before, after))
    for a in (before, after):
        print(f"v{a['version']}: recovered={a['recovered']} calls={len(a['steps'])} "
              f"tokens={a['tokens']}  {a['output'][:90]!r}")
    print(f"-> {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
