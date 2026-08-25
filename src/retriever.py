"""
retriever.py — Search over the two endorsement collections.

  • search(query, strategy, n_results, where_filter) — one vector search
  • metadata_filter_demo(query, policy_line)         — same query, with/without filter
  • hit_in_top5(...)                                 — the scoring rule for the 8 questions
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from indexer import get_collection


def search(
    query: str,
    strategy: str = "structure_aware",
    n_results: int = 5,
    where_filter: dict | None = None,
) -> list[dict]:
    """
    Vector search against one collection.

    Args:
        query:        the search string.
        strategy:     "naive" | "structure_aware"
        n_results:    how many chunks to return.
        where_filter: optional ChromaDB metadata filter, e.g.
                      {"policy_line": {"$eq": "homeowners"}}

    Returns:
        List of dicts: rank, chunk_id, score, distance, text, metadata.
    """
    result = get_collection(strategy).query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
        where=where_filter,  # None == unfiltered
    )

    rows = zip(
        result["ids"][0],
        result["documents"][0],
        result["metadatas"][0],
        result["distances"][0],
    )
    return [
        {
            "rank": rank,
            "chunk_id": chunk_id,
            "score": round(1 - distance, 4),  # cosine similarity — higher is better
            "distance": round(distance, 4),
            "text": document,
            "metadata": metadata,
        }
        for rank, (chunk_id, document, metadata, distance) in enumerate(rows, start=1)
    ]


def metadata_filter_demo(
    query: str,
    policy_line: str,
    strategy: str = "structure_aware",
    n_results: int = 5,
) -> dict:
    """Run one query twice — unfiltered, then filtered to a single policy_line."""
    return {
        "unfiltered": search(query, strategy=strategy, n_results=n_results),
        "filtered": search(
            query,
            strategy=strategy,
            n_results=n_results,
            where_filter={"policy_line": {"$eq": policy_line}},
        ),
    }


def hit_in_top5(
    query: str,
    expected_form: str,
    expected_clause_fragment: str,
    strategy: str,
    n_results: int = 5,
) -> dict:
    """
    A hit means some top-N result is BOTH from the expected form_number AND
    contains the expected clause fragment. Matching on only one of the two
    would let a lucky near-miss count as a win.
    """
    results = search(query, strategy=strategy, n_results=n_results)
    hit = next(
        (
            r
            for r in results
            if r["metadata"].get("form_number") == expected_form
            and expected_clause_fragment.lower() in r["text"].lower()
        ),
        None,
    )
    return {
        "hit": hit is not None,
        "rank": hit["rank"] if hit else None,
        "results": results,
    }


def format_results(results: list[dict], max_text_chars: int = 200) -> str:
    """Human-readable dump of a result list, for terminal output."""
    lines = []
    for r in results:
        meta = r["metadata"]
        snippet = r["text"][:max_text_chars].replace("\n", " ")
        lines.append(
            f"  Rank {r['rank']} | score={r['score']:.4f} | chunk_id={r['chunk_id']}\n"
            f"           form={meta.get('form_number', '?')} | "
            f"clause={meta.get('clause_id', '?')} | "
            f"file={meta.get('source_file', '?')}\n"
            f"           snippet: {snippet}..."
        )
    return "\n".join(lines)
