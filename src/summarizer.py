"""
summarizer.py — Week 6: the claim summary the judge is asked to grade.

Adjuster notes in, a headed claim summary out. It runs through the same live
pieces as the Q&A path — fused RRF retrieval, the Groq model at temperature
0, the paced/retried call — so the summary is the app's output, not a
separate toy built for the eval.
"""

import hashlib
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from answerer import MODEL, format_context
from hybrid import fused_search
from prompts import ACTIVE_SUMMARY_PROMPT_VERSION, render_summary
from redaction import redact
from tracing import N_RESULTS, STRATEGY, TEMPERATURE, call_model, corpus_fingerprint

SUMMARY_MAX_TOKENS = 1600   # gpt-oss spends part of the budget reasoning


def sha16(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def summarize_claim(notes_raw: str, n_results: int = N_RESULTS) -> dict:
    """
    Redact, retrieve on the notes, generate one summary.

    Claimant names, phones, emails, addresses and policy numbers are removed
    before the notes go anywhere. The claim number is kept: the summary has to
    echo it, and it is the one field the claims handler files by.
    """
    notes, redaction_counts = redact(notes_raw, keep=("claim_number",))

    hits = fused_search(notes, strategy=STRATEGY, n_results=n_results)
    messages, prompt_sha = render_summary(notes, format_context(hits))

    response, generation_ms = call_model(
        messages, model=MODEL, temperature=TEMPERATURE, max_tokens=SUMMARY_MAX_TOKENS,
    )
    summary = (response.choices[0].message.content or "").strip()

    return {
        "notes_redacted": notes,
        "redaction_counts": redaction_counts,
        "retrieval": {
            "mode": "fused_rrf",
            "strategy": STRATEGY,
            "n_results": n_results,
            "corpus_fingerprint": corpus_fingerprint(STRATEGY),
            "hits": [
                {
                    "rank": h["rank"],
                    "chunk_id": h["chunk_id"],
                    "score": h["score"],
                    "form_number": h["metadata"].get("form_number"),
                    "clause_id": h["metadata"].get("clause_id"),
                }
                for h in hits
            ],
        },
        "prompt": {"version": ACTIVE_SUMMARY_PROMPT_VERSION, "rendered_sha256": prompt_sha},
        "model": {"name": MODEL, "temperature": TEMPERATURE, "max_tokens": SUMMARY_MAX_TOKENS},
        "output": summary,
        "output_sha256": sha16(summary),
        "finish_reason": response.choices[0].finish_reason,
        "latency_ms": generation_ms,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
