#!/usr/bin/env python3
"""
mcp_agent.py — Week 9: the claims agent as an MCP host.

The agent knows no tool by name. At start-up it reads an MCP config, launches
every server listed there over stdio, runs initialize -> tools/list on each, and
hands the model exactly the tools those servers declared. A tools/call goes back
to whichever server declared that tool. Adding a server is therefore a config
change and nothing else: this file does not change.

    python src/mcp_agent.py --list-tools                       # discovery only, no model call
    python src/mcp_agent.py --query "Triage claim CLM-2024-60337" --trace week9/run.json
    python src/mcp_agent.py --config week9/some_config.json --query "..."

Where the model call happens: here, in `run()`, via tracing.call_model — the
host. Never in a server, and never on the MCP wire: the servers answer
tools/list and tools/call and nothing else.

The four Week-7 budgets still apply (BudgetLedger), so a server that returns
something the model keeps re-asking about cannot spin the loop.
"""

import argparse
import asyncio
import json
import os
import sys
import time
from contextlib import AsyncExitStack

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from agent_loop import AGENT_TEMPERATURE, DEFAULT_BUDGETS, BudgetLedger
from answerer import MODEL
from claims import CONTRACT
from tracing import call_model

DEFAULT_CONFIG = os.path.join(ROOT, "mcp_config.json")
MAX_TOKENS = 900
MAX_RESULT_CHARS = 6000

SYSTEM_PROMPT = f"""You are an assistant for an insurance claims department.

Your tools were discovered at start-up from the claims department's MCP servers.
Their descriptions are the only documentation you have: read them and choose a
tool by what its description says it does.

Rules:
- A coverage decision must come from policy wording you actually read through a
  tool. Cite the clause or exclusion ids you read.
- If none of your tools can load the claim record or its adjuster notes, do not
  guess at the facts of the loss: STATUS is REFER and REASON says what was missing.
- A claim with no adjuster notes on file is REFER.
- Payable is the covered amount minus the excess, never below $0. A denied claim
  pays $0.
- When a tool returns an error, read it. If it says how to fix the call, fix it
  and retry once.

When asked to triage a claim, answer in exactly this form and nothing else:

{CONTRACT}
"""


# ---------------------------------------------------------------------------
# discovery
# ---------------------------------------------------------------------------

def load_config(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)["mcpServers"]


def _params(spec: dict) -> StdioServerParameters:
    command = spec["command"]
    if command in ("python", "python3"):
        command = sys.executable          # the venv that runs the host runs the servers
    return StdioServerParameters(command=command, args=list(spec.get("args", [])),
                                 env=spec.get("env"), cwd=spec.get("cwd", ROOT))


class Toolbox:
    """Every configured server, connected, and the tools each one declared."""

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.stack = AsyncExitStack()
        self.sessions: dict[str, ClientSession] = {}
        self.owner: dict[str, str] = {}             # tool name -> server name
        self.tools: dict[str, object] = {}          # tool name -> mcp Tool

    async def __aenter__(self):
        for server, spec in load_config(self.config_path).items():
            read, write = await self.stack.enter_async_context(stdio_client(_params(spec)))
            session = await self.stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            self.sessions[server] = session
            listed = await session.list_tools()
            for tool in listed.tools:
                if tool.name in self.owner:
                    raise RuntimeError(f"tool {tool.name!r} is declared by both "
                                       f"{self.owner[tool.name]!r} and {server!r}")
                self.owner[tool.name] = server
                self.tools[tool.name] = tool
        return self

    async def __aexit__(self, *exc):
        await self.stack.aclose()

    def discovered(self) -> dict[str, list[str]]:
        out: dict[str, list[str]] = {s: [] for s in self.sessions}
        for name, server in self.owner.items():
            out[server].append(name)
        return out

    def schemas(self) -> list[dict]:
        """The discovered tools, as the chat-completions API wants them."""
        return [{"type": "function",
                 "function": {"name": t.name, "description": t.description or "",
                              "parameters": t.input_schema}}
                for t in self.tools.values()]

    async def call(self, name: str, args: dict) -> tuple[str | None, bool, str]:
        """(server, is_error, text). An unknown tool is an error the model sees."""
        server = self.owner.get(name)
        if server is None:
            return None, True, f"no tool named {name!r} was discovered"
        result = await self.sessions[server].call_tool(name, args)
        text = "\n".join(c.text for c in result.content if getattr(c, "text", None))
        return server, bool(result.is_error), text


# ---------------------------------------------------------------------------
# the loop
# ---------------------------------------------------------------------------

async def run(query: str, config_path: str = DEFAULT_CONFIG,
              budgets: dict | None = None) -> dict:
    budgets = dict(DEFAULT_BUDGETS if budgets is None else budgets)
    ledger = BudgetLedger(budgets)
    async with Toolbox(config_path) as box:
        tools = box.schemas()
        messages = [{"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": query}]
        calls: list[dict] = []
        output, stop_reason = "", "answered"

        while True:
            fired = ledger.check()
            if fired is not None:
                stop_reason = f"budget:{fired}"
                break
            final_lap = ledger.laps + 1 >= budgets["max_iterations"]
            response, latency_ms = call_model(
                messages, model=MODEL, temperature=AGENT_TEMPERATURE, max_tokens=MAX_TOKENS,
                tools=tools or None, tool_choice="none" if (final_lap and tools) else None)
            usage = response.usage
            ledger.record(int(usage.prompt_tokens or 0) if usage else 0,
                          int(usage.completion_tokens or 0) if usage else 0,
                          latency_ms / 1000.0)
            message = response.choices[0].message
            messages.append({"role": "assistant", "content": message.content or "",
                             **({"tool_calls": [tc.model_dump() for tc in message.tool_calls]}
                                if message.tool_calls else {})})
            if not message.tool_calls:
                output = (message.content or "").strip()
                break

            started = time.monotonic()
            for tc in message.tool_calls:
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {"_unparseable": tc.function.arguments}
                server, is_error, text = await box.call(tc.function.name, args)
                calls.append({"lap": ledger.laps, "server": server, "tool": tc.function.name,
                              "args": args, "is_error": is_error, "result": text})
                messages.append({"role": "tool", "tool_call_id": tc.id,
                                 "content": json.dumps({"is_error": is_error, "content": text},
                                                       ensure_ascii=False)[:MAX_RESULT_CHARS]})
            ledger.app_time_s += time.monotonic() - started

        return {"query": query,
                "config": os.path.relpath(config_path, ROOT),
                "discovered": box.discovered(),
                "tool_count": len(box.tools),
                "calls": calls,
                "output": output,
                "stop_reason": stop_reason,
                "usage": ledger.snapshot(),
                "model": MODEL}


async def discover(config_path: str = DEFAULT_CONFIG) -> dict[str, list[dict]]:
    """tools/list on every configured server, no model call."""
    async with Toolbox(config_path) as box:
        return {server: [{"name": n, "description": box.tools[n].description}
                         for n in names]
                for server, names in box.discovered().items()}


def main() -> None:
    load_dotenv(os.path.join(ROOT, ".env"))
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=DEFAULT_CONFIG)
    ap.add_argument("--query")
    ap.add_argument("--list-tools", action="store_true")
    ap.add_argument("--trace", help="write the run record here as JSON")
    args = ap.parse_args()

    if args.list_tools or not args.query:
        found = asyncio.run(discover(args.config))
        n = sum(len(v) for v in found.values())
        print(f"{n} tool(s) from {len(found)} server(s) via tools/list:")
        for server, tools in found.items():
            for t in tools:
                print(f"  {server:<16} {t['name']}")
        return

    record = asyncio.run(run(args.query, args.config))
    print(f"discovered {record['tool_count']} tool(s): {record['discovered']}")
    for c in record["calls"]:
        flag = "ERROR" if c["is_error"] else "ok"
        print(f"  lap {c['lap']}  {c['server']}.{c['tool']}  {json.dumps(c['args'])}  -> {flag}")
    print(f"\n{record['output']}\n\nstop={record['stop_reason']}  "
          f"laps={record['usage']['laps']}  tokens={record['usage']['total_tokens']}")
    if args.trace:
        os.makedirs(os.path.dirname(os.path.abspath(args.trace)), exist_ok=True)
        with open(args.trace, "w", encoding="utf-8") as fh:
            json.dump(record, fh, indent=2, ensure_ascii=False)
        print(f"-> {args.trace}")


if __name__ == "__main__":
    main()
