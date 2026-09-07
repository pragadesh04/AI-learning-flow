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
