#!/usr/bin/env python3
"""
capture_wire.py — Week 9: the raw JSON-RPC exchange against the claims-system server.

No SDK client: this spawns the server exactly as mcp_config.json says, writes
newline-delimited JSON-RPC to its stdin and reads its stdout, so every byte on
the wire is recorded as sent and received.

    initialize -> notifications/initialized -> tools/list -> tools/call

    python week9/capture_wire.py        # -> week9/wire_raw.json

There is no model anywhere in this exchange. The model call happens in the host
(src/mcp_agent.py, run() -> tracing.call_model), never on this wire.
"""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))

from mcp.types import LATEST_PROTOCOL_VERSION

OUT = os.path.join(HERE, "wire_raw.json")
CLAIM = "CLM-2024-60337"

SEQUENCE = [
    {"jsonrpc": "2.0", "id": 1, "method": "initialize",
     "params": {"protocolVersion": LATEST_PROTOCOL_VERSION, "capabilities": {},
                "clientInfo": {"name": "week9-wire-capture", "version": "1.0"}}},
    {"jsonrpc": "2.0", "method": "notifications/initialized"},
    {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
    {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
     "params": {"name": "get_claim_status", "arguments": {"claim_number": CLAIM}}},
]


def main() -> None:
    with open(os.path.join(ROOT, "mcp_config.json"), encoding="utf-8") as fh:
        spec = json.load(fh)["mcpServers"]["claims-system"]
    proc = subprocess.Popen([sys.executable, *spec["args"]], cwd=ROOT,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, text=True, encoding="utf-8")
    exchange = []
    for msg in SEQUENCE:
        line = json.dumps(msg)
        proc.stdin.write(line + "\n")
        proc.stdin.flush()
        entry = {"direction": "client -> server", "raw": line, "message": msg}
        if "id" in msg:                       # a request: read until its response
            while True:
                raw = proc.stdout.readline()
                if not raw:
                    raise RuntimeError("server closed stdout")
                reply = json.loads(raw)
                if reply.get("id") == msg["id"]:
                    break
                exchange.append({"direction": "server -> client", "raw": raw.rstrip("\n"),
                                 "message": reply, "note": "unsolicited"})
            exchange.append(entry)
            exchange.append({"direction": "server -> client", "raw": raw.rstrip("\n"),
                             "message": reply})
        else:                                 # a notification: no response by design
            exchange.append(entry)
    proc.stdin.close()
    proc.wait(timeout=10)

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(exchange, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    for e in exchange:
        print(f"{e['direction']:<17} {e['raw'][:150]}")
    print(f"-> {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
