import difflib
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from answerer import REFUSAL_PREFIX
from indexer import resolve_chunk
from tracing import call_model, corpus_fingerprint

RULE = "=" * 78


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def rebuild_context(trace: dict) -> tuple[str, list[str]]:
    """
    Rebuild the context block the model saw, from chunk_ids + scores alone.

    Mirrors answerer.format_context exactly. Returns the block and a list of
    problems (a chunk_id that no longer resolves, or text whose hash has moved
    since the trace was written).
    """
    strategy = trace["retrieval"]["strategy"]
    problems, blocks = [], []

    for hit in trace["retrieval"]["hits"]:
        chunk = resolve_chunk(hit["chunk_id"], strategy=strategy)
        if chunk is None:
            problems.append(f"chunk_id {hit['chunk_id']} no longer resolves in the index")
            continue
        recorded = hit.get("text_sha256")            # v1.1 only
        if recorded and recorded != sha(chunk["text"]):
            problems.append(f"chunk {hit['chunk_id']} text has changed since the trace")
        meta = chunk["metadata"]
        blocks.append(
            f"--- CHUNK ---\n"
            f"chunk_id: {hit['chunk_id']}\n"
            f"form_number: {meta.get('form_number', 'UNKNOWN')}\n"
            f"clause_id: {meta.get('clause_id', 'N/A')}\n"
            f"source_file: {meta.get('source_file', 'UNKNOWN')}\n"
            f"score: {hit['score']:.4f}\n"
            f"text:\n{chunk['text']}\n"
        )
    return "\n".join(blocks), problems


def build_messages(trace: dict, context_block: str) -> tuple[list[dict], dict]:
    """
    Rebuild system + user messages, and report the provenance of each part.

    v1.0 traces carry no prompt version, so the system prompt and the user
    template can only come FROM CODE — the replay assumes today's source is
    what ran, and cannot prove it.
    """
    provenance = {}

    if "prompt" in trace:                                   # schema v1.1
        from prompts import PROMPT_VERSIONS

        version = trace["prompt"]["version"]
        spec = PROMPT_VERSIONS[version]
        provenance["system prompt"] = f"FROM TRACE (prompt_version={version})"
        provenance["user template"] = f"FROM TRACE (prompt_version={version})"
        system, template = spec["system"], spec["user_template"]
    else:                                                   # schema v1.0
        from answerer import SYSTEM_PROMPT, USER_TEMPLATE

        provenance["system prompt"] = "FROM CODE (trace has no prompt_version)"
        provenance["user template"] = "FROM CODE (trace has no prompt_version)"
        system, template = SYSTEM_PROMPT, USER_TEMPLATE

    user = template.format(context=context_block, question=trace["question"])
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    return messages, provenance


def replay_trace(trace: dict, live: bool = True) -> dict:
    """Reconstruct, optionally re-run, and print the original next to the replay."""
    schema = trace["schema_version"]
    print(RULE)
    print(f"REPLAY OF {trace['trace_id']}   (trace schema v{schema})")
    print(RULE)

    context_block, problems = rebuild_context(trace)
    messages, provenance = build_messages(trace, context_block)

    prov = {
        "question (redacted)": "FROM TRACE",
        "retrieved chunk_ids + scores": "FROM TRACE",
        "chunk text": "FROM INDEX (resolved by chunk_id)",
        **provenance,
        "model name": "FROM TRACE",
        "temperature / max_tokens": "FROM TRACE",
        "original raw output": "FROM TRACE",
    }
    if "prompt" in trace:
        prov["prompt hash check"] = (
            "MATCH" if sha(messages[0]["content"] + messages[1]["content"])
            == trace["prompt"]["rendered_sha256"] else "MISMATCH"
        )
        recorded_fp = trace["retrieval"].get("corpus_fingerprint")
        live_fp = corpus_fingerprint(trace["retrieval"]["strategy"])
        prov["corpus fingerprint"] = (
            f"MATCH ({live_fp})" if recorded_fp == live_fp
            else f"MISMATCH trace={recorded_fp} now={live_fp}"
        )
    else:
        prov["prompt hash check"] = "UNRECOVERABLE (v1.0 stored no rendered prompt hash)"
        prov["corpus fingerprint"] = "UNRECOVERABLE (v1.0 stored no fingerprint)"
    prov["provider-side sampling seed"] = "UNRECOVERABLE (Groq does not echo it back)"

    print("\nRECONSTRUCTION MANIFEST")
    for field, source in prov.items():
        print(f"  {field:<30s} {source}")
    for problem in problems:
        print(f"  !! {problem}")

    print(f"\n  rebuilt prompt: {len(messages[0]['content'])} char system + "
          f"{len(messages[1]['content'])} char user  "
          f"(sha256 {sha(messages[0]['content'] + messages[1]['content'])[:16]})")

    original = trace["output"]["raw"]
    if not live:
        print("\n  --dry-run: reconstruction only, no API call made.")
        return {"replayed": None, "identical": None}

    model = trace["model"]
    response, _ = call_model(          # paced and retried against the token budget
        messages,
        model=model["name"],
        temperature=model["temperature"],
        max_tokens=model["max_tokens"],
    )
    replayed = (response.choices[0].message.content or "").strip()

    identical = replayed == original
    ratio = difflib.SequenceMatcher(None, original, replayed).ratio()

    print(f"\n{RULE}\nORIGINAL OUTPUT (from the trace, {trace['ts']})\n{RULE}")
    print(original)
    print(f"\n{RULE}\nREPLAYED OUTPUT (re-run just now)\n{RULE}")
    print(replayed)
    print(f"\n{RULE}")
    print(f"identical: {identical}    similarity: {ratio:.4f}    "
          f"refusal original={trace['output']['is_refusal']} "
          f"replayed={replayed.startswith(REFUSAL_PREFIX)}")
    if not identical:
        print("\nunified diff (original -> replayed):")
        for line in difflib.unified_diff(
            original.splitlines(), replayed.splitlines(),
            fromfile="original", tofile="replayed", lineterm="", n=1
        ):
            print("  " + line)
    print(RULE)

    return {"replayed": replayed, "identical": identical, "similarity": ratio}
