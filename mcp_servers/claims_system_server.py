#!/usr/bin/env python3
"""
claims_system_server.py — Week 9, server two: the claims platform team's MCP server.

In the brief this server is third-party: the claims platform team stood it up
and the assistant is meant to start using it without a code release. It lives
in this repo only so the course can run it; treat it as code we did not write
and do not own (see week9/risk_note.md).

    tools   get_claim_status     the claim record and its workflow status
            get_adjuster_notes   the adjuster note history behind a claim

No model call happens here either. Every tools/call is appended to
week9/logs/claims_server.log (time, tool, claim number) — the log records which
claims were looked up, never the note text.
"""

import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "src"))

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from claims import CLAIMS, by_number
from redaction import redact

LOG = os.path.join(ROOT, "week9", "logs", "claims_server.log")

# The workflow status the platform holds for each claim. A claim with no notes
# on file is still open: nobody has inspected it.
STATUS = {c["claim_number"]: ("open" if not c["notes_present"] else "under_review")
          for c in CLAIMS}

mcp = MCPServer("claims-system",
                instructions="Claim records and adjuster note history from the claims platform.")


def _audit(tool: str, claim_number: str) -> None:
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "tool": tool,
                             "claim_number": claim_number}) + "\n")


def _claim(claim_number: str) -> dict:
    claim = by_number(claim_number.strip())
    if claim is None:
        raise ToolError(f"claim {claim_number!r} not found: claim numbers look like "
                        f"CLM-YYYY-NNNNN, e.g. CLM-2024-31842")
    return claim


@mcp.tool(name="get_claim_status")
def get_claim_status(claim_number: str) -> dict:
    """Return the claim record filed under one claim number: workflow status,
    policy forms in force, date of loss, amount claimed and the excess on file.
    Does not return adjuster notes or policy wording."""
    _audit("get_claim_status", claim_number)
    c = _claim(claim_number)
    return {"claim_number": c["claim_number"], "status": STATUS[c["claim_number"]],
            "policy_forms": c["policy_forms"], "date_of_loss": c["date_of_loss"],
            "amount_claimed_usd": c["amount_claimed_usd"], "excess_usd": c["excess_usd"],
            "coverage_a_limit_usd": c["coverage_a_limit_usd"]}


@mcp.tool(name="get_adjuster_notes")
def get_adjuster_notes(claim_number: str) -> dict:
    """Return the adjuster note history for one claim number, oldest first.
    An empty history means no adjuster has inspected the claim yet."""
    _audit("get_adjuster_notes", claim_number)
    c = _claim(claim_number)
    if not c["notes_present"]:
        return {"claim_number": c["claim_number"], "notes": []}
    text, _ = redact(c["adjuster_notes"], keep=("claim_number",))
    return {"claim_number": c["claim_number"],
            "notes": [{"seq": 1, "entered": c["date_of_loss"], "author": "field adjuster",
                       "text": text}]}


if __name__ == "__main__":
    mcp.run()
