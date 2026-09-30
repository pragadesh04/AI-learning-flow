import hashlib
import json
import os
import random
import re
import sys
import threading
import time
from datetime import datetime
from functools import lru_cache

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from answerer import MODEL, REFUSAL_PREFIX, format_context, get_client
from hybrid import fused_search
from indexer import get_collection
from prompts import ACTIVE_PROMPT_VERSION, render
from redaction import assert_clean, redact

SCHEMA_VERSION = "1.1"

HERE = os.path.dirname(os.path.abspath(__file__))
TRACE_DIR = os.path.join(HERE, "..", "traces")
DEFAULT_LOG = os.path.join(TRACE_DIR, "traffic.jsonl")

# Generation params, held here so the trace records what was actually sent.
TEMPERATURE = 0.0
MAX_TOKENS = 800
RETRIEVAL_MODE = "fused_rrf"
STRATEGY = "structure_aware"
N_RESULTS = 5


# ---------------------------------------------------------------------------
# Throttle — the Groq free tier caps this model at 8,000 tokens per minute,
# which is about three of these calls. A batch run that ignores that spends
# its wall clock collecting 429s, so the budget is tracked here instead.
# ---------------------------------------------------------------------------

TPM_LIMIT = int(os.environ.get("GROQ_TPM_LIMIT", "8000"))

_pace_lock = threading.Lock()
_write_lock = threading.Lock()
_next_slot = 0.0            # monotonic time the next call may start
_avg_tokens = 2200.0        # seeded, then learned from response.usage


def _pace(estimate: int) -> None:
    """
    Hold the next call until its share of the token budget has accrued.

    A rolling-window ledger looks more precise and behaves worse: when the
    window fills, every worker blocks for the remainder of the minute, and a
    429 on top of that costs a second full wait. Spacing calls evenly by
    observed token cost keeps the pipe full instead.
    """
    global _next_slot
    with _pace_lock:
        now = time.monotonic()
        start_at = max(now, _next_slot)
        interval = 60.0 * max(_avg_tokens, float(estimate)) / TPM_LIMIT
        _next_slot = start_at + interval
    delay = start_at - time.monotonic()
    if delay > 0:
        time.sleep(delay)


def _observe(total_tokens: int) -> None:
    """Learn what a call really costs, so the spacing tracks reality."""
    global _avg_tokens
    with _pace_lock:
        _avg_tokens = 0.7 * _avg_tokens + 0.3 * float(total_tokens)


def _defer(seconds: float) -> None:
    """Push the next slot back after the provider says to wait."""
    global _next_slot
    with _pace_lock:
        _next_slot = max(_next_slot, time.monotonic() + seconds)


_RETRY_AFTER = re.compile(r"try again in ([\d.]+)s")
_TPD_LIMIT = re.compile(r"tokens per day \(TPD\): Limit (\d+), Used (\d+)")


# The free tier also caps tokens per DAY, and that limit releases in small
# increments over minutes. A batch run therefore has to be patient, not fast.
MAX_ATTEMPTS = int(os.environ.get("GROQ_MAX_ATTEMPTS", "24"))


class DailyTokenLimit(RuntimeError):
    """
    The account's daily token allowance is spent.

    Distinct from a per-minute 429 for a reason that costs real time: a
    per-minute limit clears in seconds and is worth retrying, while a daily
    limit clears in hours and retrying it just burns the wall clock before
    failing the same way. So this one is raised on the first refusal instead of
    being queued behind `MAX_ATTEMPTS` sleeps.
    """

    def __init__(self, limit: int, used: int):
        self.limit, self.used = limit, used
        self.remaining = max(0, limit - used)
        super().__init__(
            f"Groq daily token allowance is spent: {used:,} of {limit:,} used, "
            f"{self.remaining:,} left. This is a per-DAY cap, so retrying will not "
            f"help — it resets on the account's next UTC day. Either wait for the "
            f"reset or run the arm on a key with a paid tier."
        )


def call_model(messages: list[dict], model: str, temperature: float, max_tokens: int,
               attempts: int = MAX_ATTEMPTS, tools: list[dict] | None = None,
               tool_choice: str | None = None
               ) -> tuple[object, float]:
    """
    One chat completion, paced against the token budget and retried on 429.

    `tools` (Week 7) switches the request from generation to a tool-calling
    lap. It defaults to None so every existing caller is byte-identical.
    `tool_choice` is only sent when set; "none" is the one that matters — it
    tells the provider to refuse a tool call server-side, which is the only
    way to guarantee a text answer on a lap that is out of tool budget.

    Returns the response and the latency of the successful call ONLY — waiting
    for the token budget is a property of the free tier, not of the app, and
    folding it into the latency figure would make every trace unreadable.
    """
    estimate = sum(len(m["content"]) for m in messages) // 4 + 400
    if tools:
        estimate += len(json.dumps(tools)) // 4
    body = {"tools": tools}
    if tool_choice is not None:
        body["tool_choice"] = tool_choice
    for attempt in range(1, attempts + 1):
        _pace(estimate)
        try:
            started = time.perf_counter()
            response = get_client().chat.completions.create(
                model=model, messages=messages,
                temperature=temperature, max_tokens=max_tokens,
                **body,
            )
            elapsed_ms = round((time.perf_counter() - started) * 1000, 1)
            if response.usage:
                _observe(response.usage.total_tokens)
            return response, elapsed_ms
        except Exception as exc:
            text = str(exc)
            if "rate_limit" not in text and "429" not in text:
                raise
            tpd = _TPD_LIMIT.search(text)
            if tpd:
                raise DailyTokenLimit(int(tpd.group(1)), int(tpd.group(2))) from exc
            if attempt == attempts:
                raise
            match = _RETRY_AFTER.search(text)
            _defer((float(match.group(1)) if match else 15.0) + random.uniform(0.5, 2.0))


@lru_cache(maxsize=4)
def corpus_fingerprint(strategy: str = STRATEGY) -> str:
    """
    A hash over every (chunk_id, text) pair in a collection.

    Stored on every trace so a replay can tell "the index still holds what it
    held" from "someone re-chunked the corpus and these chunk_ids now resolve
    to different text". Cached; call cache_clear() after re-ingesting.
    """
    data = get_collection(strategy).get(include=["documents"])
    pairs = sorted(zip(data["ids"], data["documents"]))
    digest = hashlib.sha256()
    for chunk_id, text in pairs:
        digest.update(chunk_id.encode("utf-8"))
        digest.update(text.encode("utf-8"))
    return f"sha256:{digest.hexdigest()[:16]}:{len(pairs)}"


def trace_id(ts: datetime, seq: int) -> str:
    """Sortable and human-readable: tr_20260901T0914_0007."""
    return f"tr_{ts.strftime('%Y%m%dT%H%M')}_{seq:04d}"


def _hit_row(hit: dict) -> dict:
    """The retrieval evidence kept per chunk: what came back and how well."""
    meta = hit.get("metadata", {})
    return {
        "rank": hit["rank"],
        "chunk_id": hit["chunk_id"],
        "score": hit["score"],
        "dense_rank": hit.get("dense_rank"),
        "bm25_rank": hit.get("bm25_rank"),
        "form_number": meta.get("form_number"),
        "edition_date": meta.get("edition_date"),
        "clause_id": meta.get("clause_id"),
        "source_file": meta.get("source_file"),
        # v1.1: proves this chunk's text is the text the model actually saw
        "text_sha256": hashlib.sha256(hit["text"].encode("utf-8")).hexdigest()[:16],
    }


def answer_and_trace(
    question_raw: str,
    *,
    channel: str = "adjuster_desk",
    session_id: str = "unknown",
    ts: datetime | None = None,
    seq: int = 0,
    log_path: str | None = DEFAULT_LOG,
    n_results: int = N_RESULTS,
) -> dict:
    """
    Answer one question through the live pipeline and append one trace line.

    `question_raw` may contain claimant identifiers; they are removed here,
    before anything is retrieved with them or written down.

    log_path=None returns the record without writing it — the batch simulator
    uses that to collect concurrently and write the log in timestamp order.
    """
    ts = ts or datetime.now()

    question, redaction_counts = redact(question_raw)

    t0 = time.perf_counter()
    hits = fused_search(question, strategy=STRATEGY, n_results=n_results)
    retrieval_ms = round((time.perf_counter() - t0) * 1000, 1)

    # The registry renders the request and hands back the hash that identifies
    # it, so the trace names the wording instead of assuming it.
    messages, prompt_sha = render(question, format_context(hits))

    response, generation_ms = call_model(
        messages,
        model=MODEL,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )
    raw_output = (response.choices[0].message.content or "").strip()

    record = {
        "schema_version": SCHEMA_VERSION,
        "trace_id": trace_id(ts, seq),
        "ts": ts.isoformat(timespec="seconds"),
        "channel": channel,
        "session_id": session_id,
        "question": question,
        "redaction": {
            "applied": bool(redaction_counts),
            "counts": redaction_counts,
            "stage": "pre_write",
        },
        "retrieval": {
            "mode": RETRIEVAL_MODE,
            "strategy": STRATEGY,
            "n_results": n_results,
            "latency_ms": retrieval_ms,
            "corpus_fingerprint": corpus_fingerprint(STRATEGY),
            "hits": [_hit_row(h) for h in hits],
        },
        "prompt": {
            "version": ACTIVE_PROMPT_VERSION,
            "rendered_sha256": prompt_sha,
        },
        "model": {
            "provider": "groq",
            "name": MODEL,
            "temperature": TEMPERATURE,
            "max_tokens": MAX_TOKENS,
        },
        "output": {
            "raw": raw_output,
            "is_refusal": raw_output.startswith(REFUSAL_PREFIX),
            "latency_ms": generation_ms,
            "finish_reason": response.choices[0].finish_reason,
            "response_id": response.id,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            } if response.usage else None,
        },
    }

    if log_path is not None:
        write_trace(record, log_path)
    return record


def write_trace(record: dict, log_path: str = DEFAULT_LOG) -> None:
    """Serialise, guard, then append. The guard is why the file is safe to commit."""
    line = json.dumps(record, ensure_ascii=False)
    assert_clean(line, where=f"trace {record.get('trace_id')}")
    os.makedirs(os.path.dirname(os.path.abspath(log_path)), exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def read_traces(log_path: str = DEFAULT_LOG) -> list[dict]:
    """Every trace in one log, in write order."""
    if not os.path.exists(log_path):
        return []
    with open(log_path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]
