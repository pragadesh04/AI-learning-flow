#!/usr/bin/env python3
"""
policy_server.py — Week 9, server one: OUR policy-document MCP server.

Exposes the indexed endorsement wording over MCP (stdio). It is a capability,
not a decision-maker: there is no model call anywhere in this file. The host
(src/mcp_agent.py) runs the model; this process only answers tools/call and
resources/read.

    tools       search_policy                     model-invoked
    resources   policy://forms                    app-attached
                policy://{form_number}/exclusions app-attached

The exclusion schedules are RESOURCES, not tools, on purpose: they are context
the application should attach, not something the model should have to go and
fetch. A tool would invite the model to call out for a table it should already
have been given.

POLICY_SERVER_VERSION selects the search_policy contract, so the Week-9 error
rewrite can be re-run either way from config alone:

    1   the original: one-line docstring, and an unknown form raises a bare
        exception, which the SDK reports to the model as
        "Error executing tool search_policy" — no cause, no way to recover
    2   (default) the docstring rewritten as a prompt, and the unknown-form
        path raised as a ToolError that says what a form number looks like and
        which ones exist
"""

import contextlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "src"))

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from claims import FORMS

VERSION = os.environ.get("POLICY_SERVER_VERSION", "2")
ENDORSEMENTS = os.path.join(ROOT, "endorsements")
N_RESULTS = 3
MAX_CHUNK_CHARS = 2000

SEARCH_POLICY_DESC_V1 = "Search the policy."

SEARCH_POLICY_DESC_V2 = """Search the indexed endorsement wording for the clause that governs ONE peril on ONE form.

Use this after you know (a) which policy forms are on the claim and (b) what the
peril is. It returns up to 3 passages, each with its form_number, clause_id and
the exclusion-table text, so you can quote the code (e.g. E-12) that decides
the claim.

Arguments:
  query        the peril in plain words, e.g. "flood from surface water through
               the garage door". Not a code: searching "E-12" five ways returns
               the same row five times.
  form_number  exactly one indexed form, four digits after "HO-": HO-0304,
               HO-0305, HO-0306, HO-0307, HO-0308 or HO-0309. Take it from the
               claim file; never guess one. A claim on two forms needs two calls.

This tool knows nothing about any individual claim and does no arithmetic.
If it returns an error, the error says how to fix the call: fix it and retry
once, do not answer coverage without wording."""

mcp = MCPServer(
    "policy-docs",
    instructions="Endorsement wording for the HO-03xx water and storm forms.",
)


def _search(query: str, form: str) -> list[dict]:
    # The retriever stack prints while loading; stdout is the JSON-RPC channel.
    with contextlib.redirect_stdout(sys.stderr):
        from hybrid import fused_search
        hits = fused_search(f"{query} {form}", strategy="structure_aware",
                            n_results=N_RESULTS)
    rows = [h for h in hits if h["metadata"].get("form_number") == form] or hits[:1]
    return [{"chunk_id": h["chunk_id"],
             "form_number": h["metadata"].get("form_number"),
             "clause_id": h["metadata"].get("clause_id"),
             "text": h["text"][:MAX_CHUNK_CHARS]} for h in rows]


@mcp.tool(name="search_policy",
          description=SEARCH_POLICY_DESC_V2 if VERSION == "2" else SEARCH_POLICY_DESC_V1)
def search_policy(query: str, form_number: str) -> dict:
    form = form_number.strip().upper()
    if form not in FORMS:
        if VERSION == "2":
            raise ToolError(
                f"form {form_number!r} is not an indexed form: form numbers look like "
                f"HO-03NN, four digits after 'HO-'. Indexed forms are {', '.join(FORMS)}. "
                f"Take the form from the claim file and call search_policy again.")
        raise LookupError(3)      # v1: reaches the model as a bare "Error executing tool"
    return {"query": query, "form_number": form, "hits": _search(query, form)}


@mcp.resource("policy://forms", name="indexed_forms",
              description="The endorsement forms in the index, one per line.")
def indexed_forms() -> str:
    return "\n".join(FORMS)


@mcp.resource("policy://{form_number}/exclusions", name="exclusion_schedule",
              description="The exclusion table of one endorsement form, verbatim.")
def exclusion_schedule(form_number: str) -> str:
    form = form_number.strip().upper()
    for name in sorted(os.listdir(ENDORSEMENTS)):
        if name.startswith(form + "_"):
            with open(os.path.join(ENDORSEMENTS, name), encoding="utf-8") as fh:
                text = fh.read()
            m = re.search(r"EXCLUSION TABLE.*?(?=\nSECTION |\Z)", text, re.S)
            return m.group(0).strip() if m else f"{form} has no exclusion table"
    raise ValueError(f"unknown form {form_number!r}")


if __name__ == "__main__":
    mcp.run()
