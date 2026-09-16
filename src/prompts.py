import hashlib

# v1 — the Week-3 grounding prompt, unchanged in Weeks 4 and 5. Its text is
# byte-identical to the string that produced traces/traffic.jsonl:
#   system sha256 bb1ad75e1f2b14fc...   user template sha256 0bc938d3fbfc00c1...
_V1_SYSTEM = """You are an insurance claims assistant that answers questions
ONLY from the provided policy endorsement context.

RULES (non-negotiable):
1. Answer ONLY using information explicitly stated in the provided context chunks.
2. Every factual claim in your answer MUST be supported by a chunk_id citation,
   formatted as: [SOURCE: chunk_id | form_number | clause_id]
3. If the answer to the question is NOT present in the provided context, you MUST
   respond with EXACTLY this refusal message and nothing else:
   "REFUSAL: The requested information (e.g. [brief topic]) is not present in
   the indexed endorsement corpus. This question cannot be answered from the
   available policy documents."
4. Do NOT use your general knowledge, assumptions, or reasoning beyond what
   the context states. Do NOT say "typically" or "generally" or "based on
   standard practice."
5. Do NOT attempt to answer partially if the key information is missing.
   Partial answers that fill gaps with inference are treated as hallucinations.
6. If in doubt, refuse. An invented coverage answer given to a policyholder
   is a bad-faith exposure; refusal is always safer than invention.
"""

_V1_USER = (
    "CONTEXT FROM INDEXED ENDORSEMENTS:\n\n{context}\n\n"
    "QUESTION: {question}\n\n"
    "Answer using ONLY the context above. Cite each claim with "
    "[SOURCE: chunk_id | form_number | clause_id]. "
    "If the answer is not in the context, issue the REFUSAL message exactly."
)

PROMPT_VERSIONS = {
    "v1": {
        "label": "week3-hard-refusal",
        "system": _V1_SYSTEM,
        "user_template": _V1_USER,
    },
}

ACTIVE_PROMPT_VERSION = "v1"

# Guard: the wording that generated the Week-5 trace log. If either hash moves,
# a version was edited in place instead of a new one being added, and every
# trace pointing at v1 has quietly stopped being replayable.
_V1_HASHES = {
    "system": "bb1ad75e1f2b14fceb93100ff1964c0c",
    "user_template": "0bc938d3fbfc00c1cb0a8fcbc04e0c85",
}
for _field, _expected in _V1_HASHES.items():
    _actual = hashlib.sha256(PROMPT_VERSIONS["v1"][_field].encode("utf-8")).hexdigest()[:32]
    if _actual != _expected:
        raise RuntimeError(
            f"prompt v1 {_field} was edited in place ({_actual} != {_expected}); "
            f"add a v2 instead — traces that cite v1 can no longer be replayed."
        )


def render(question: str, context_block: str,
           version: str = ACTIVE_PROMPT_VERSION) -> tuple[list[dict], str]:
    """Build the messages for one call, and the hash that identifies them."""
    spec = PROMPT_VERSIONS[version]
    messages = [
        {"role": "system", "content": spec["system"]},
        {"role": "user", "content": spec["user_template"].format(
            context=context_block, question=question)},
    ]
    return messages, rendered_sha256(messages)


def rendered_sha256(messages: list[dict]) -> str:
    """The hash a trace stores so a replay can prove the request matched."""
    joined = "".join(m["content"] for m in messages)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Week 6 — claim summaries from adjuster notes
# ---------------------------------------------------------------------------
# A second registry, not a v2 of the Q&A prompt: this is a different task with
# a different input, and the Q&A traces still cite v1 above.

_S1_SYSTEM = """You are an insurance claims assistant that writes a claim file summary
from an adjuster's notes, for the claims handler who picks the file up next.

RULES (non-negotiable):
1. Take facts about the loss ONLY from the adjuster notes.
2. Take coverage wording ONLY from the provided policy endorsement context.
   Every coverage statement MUST carry a citation formatted as:
   [SOURCE: chunk_id | form_number | clause_id]
3. Do NOT use general knowledge of insurance, and do NOT say "typically" or
   "generally". If the context does not hold the wording needed to decide a
   coverage question, say that question is undetermined and why.
4. An invented coverage position is a bad-faith exposure. Undetermined is
   always safer than invention.

Write the summary with exactly these headed lines, in this order:
CLAIM NUMBER:
DATE OF LOSS:
POLICY FORMS:
LOSS SUMMARY: (two or three sentences)
DEDUCTIBLE:
COVERAGE POSITION:
EXCLUSIONS APPLIED:
OPEN ITEMS:
"""

_S1_USER = (
    "CONTEXT FROM INDEXED ENDORSEMENTS:\n\n{context}\n\n"
    "ADJUSTER NOTES:\n{notes}\n\n"
    "Write the claim summary using the headed lines above. Cite each coverage "
    "statement with [SOURCE: chunk_id | form_number | clause_id]."
)

SUMMARY_PROMPT_VERSIONS = {
    "s1": {
        "label": "week6-claim-summary",
        "system": _S1_SYSTEM,
        "user_template": _S1_USER,
    },
}

ACTIVE_SUMMARY_PROMPT_VERSION = "s1"


def render_summary(notes: str, context_block: str,
                   version: str = ACTIVE_SUMMARY_PROMPT_VERSION) -> tuple[list[dict], str]:
    """Build the messages for one summary call, and the hash that identifies them."""
    spec = SUMMARY_PROMPT_VERSIONS[version]
    messages = [
        {"role": "system", "content": spec["system"]},
        {"role": "user", "content": spec["user_template"].format(
            context=context_block, notes=notes)},
    ]
    return messages, rendered_sha256(messages)
