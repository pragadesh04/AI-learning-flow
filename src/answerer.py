import os
import sys
from functools import lru_cache

from openai import OpenAI

sys.path.insert(0, os.path.dirname(__file__))
from prompts import ACTIVE_PROMPT_VERSION, PROMPT_VERSIONS
from retriever import search

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
MODEL = "openai/gpt-oss-120b"
REFUSAL_PREFIX = "REFUSAL:"


@lru_cache(maxsize=1)
def get_client() -> OpenAI:
    """The Groq client. Key is read here, not at import, so .env still works."""
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is not set. Copy .env.example to .env and add your "
            "key, or export GROQ_API_KEY=gsk_... before running."
        )
    return OpenAI(api_key=api_key, base_url=GROQ_BASE_URL)


# ---------------------------------------------------------------------------
# Grounding system prompt — hard refusal, no hallucination escape hatch
# ---------------------------------------------------------------------------

_LEGACY_SYSTEM_PROMPT = """You are an insurance claims assistant that answers questions
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

# Week 5: the live prompt now comes from the versioned registry, so a trace can
# name the wording that ran and a replay can prove it. The literal above is kept
# only as a tripwire — if the registry's v1 ever drifts from the text this
# module shipped with, importing answerer fails loudly rather than quietly
# replaying traces against wording that never ran.
SYSTEM_PROMPT = PROMPT_VERSIONS[ACTIVE_PROMPT_VERSION]["system"]
USER_TEMPLATE = PROMPT_VERSIONS[ACTIVE_PROMPT_VERSION]["user_template"]

if SYSTEM_PROMPT != _LEGACY_SYSTEM_PROMPT:
    raise RuntimeError(
        "prompts.py v1 no longer matches the system prompt answerer.py shipped "
        "with; add a new prompt version instead of editing v1 in place."
    )


def format_context(hits: list[dict]) -> str:
    """Format retrieved chunks into the context block the model cites from."""
    return "\n".join(
        f"--- CHUNK ---\n"
        f"chunk_id: {h['chunk_id']}\n"
        f"form_number: {h['metadata'].get('form_number', 'UNKNOWN')}\n"
        f"clause_id: {h['metadata'].get('clause_id', 'N/A')}\n"
        f"source_file: {h['metadata'].get('source_file', 'UNKNOWN')}\n"
        f"score: {h['score']:.4f}\n"
        f"text:\n{h['text']}\n"
        for h in hits
    )


def generate_answer(question: str, hits: list[dict], verbose: bool = True) -> dict:
    """
    Generate a grounded answer — or a hard refusal — from retrieved chunks.

    Returns:
        dict with question, answer, is_refusal, hits_used.
    """
    user_message = USER_TEMPLATE.format(
        context=format_context(hits), question=question
    )

    response = get_client().chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.0,
        max_tokens=800,
    )
    answer = response.choices[0].message.content.strip()

    is_refusal = answer.startswith(REFUSAL_PREFIX)

    if verbose:
        tag = "REFUSAL" if is_refusal else "A"
        print(f"\n  Q: {question}")
        print(f"  {tag}: {answer}\n")

    return {
        "question": question,
        "answer": answer,
        "is_refusal": is_refusal,
        "hits_used": [h["chunk_id"] for h in hits],
    }


def answer_questions(
    questions: list[dict],
    n_results: int = 5,
    verbose: bool = True,
) -> list[dict]:
    """
    Retrieve then generate for each question.

    Each question is a dict with a "question" key; any extra keys (such as
    expected_form / expected_clause) are carried through to the result so the
    write-up can show them next to the answer.
    """
    results = []
    for q in questions:
        hits = search(q["question"], strategy="structure_aware", n_results=n_results)
        results.append({**q, **generate_answer(q["question"], hits, verbose=verbose)})
    return results
