#!/usr/bin/env python3
"""
inspect_retrieval.py — The inspection view for Week 4 failure labelling.

Shows, for one query or for the whole golden set, exactly what each retrieval
path returned: rank, chunk_id, clause, score, which channel surfaced it
(dense / bm25 / both), and where the known-correct chunk actually sits in the
full dense ordering. Every R/G label in results.md cites a line from here.

Usage:
    python inspect_retrieval.py "does exclusion E-17 apply under HO-0304?"
    python inspect_retrieval.py "..." --golden HO-0304_sa_chunk_007 --mode both
    python inspect_retrieval.py --golden-set golden_set.jsonl --mode dense
"""

import argparse
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from indexer import get_collection
from retriever import search
from hybrid import fused_search

TOP_K = 3


def _row(r: dict) -> str:
    meta = r["metadata"]
    channel = ""
    if "dense_rank" in r:
        channel = f" | dense#{r['dense_rank'] or '—'} bm25#{r['bm25_rank'] or '—'}"
    snippet = " ".join(r["text"].split())[:110]
    return (
        f"  #{r['rank']} {r['chunk_id']:<28s} {meta.get('clause_id', '?'):<24s} "
        f"score={r['score']:.4f}{channel}\n      {snippet}..."
    )


def deep_dense_rank(query: str, wanted: set[str]) -> tuple[int | None, str | None]:
    """Where the golden chunk really sits in the full dense ordering."""
    total = get_collection("structure_aware").count()
    for r in search(query, n_results=total):
        if r["chunk_id"] in wanted:
            return r["rank"], r["chunk_id"]
    return None, None


def show_query(query: str, golden: set[str] | None, mode: str, top: int) -> None:
    print(f"\nQUERY: {query}")
    paths = {"dense": lambda: search(query, n_results=top),
             "fused": lambda: fused_search(query, n_results=top)}
    for name in (["dense", "fused"] if mode == "both" else [mode]):
        print(f"\n--- {name.upper()} top-{top} ---")
        for r in paths[name]():
            marker = "   <-- GOLDEN" if golden and r["chunk_id"] in golden else ""
            print(_row(r) + marker)
    if golden:
        rank, cid = deep_dense_rank(query, golden)
        where = f"dense rank {rank} ({cid})" if rank else "NOT in the corpus"
        print(f"\n  golden chunk sits at: {where}")


def show_golden_set(path: str, mode: str, top: int) -> None:
    search_fn = {"dense": search, "fused": fused_search}[mode]
    hits = 0
    with open(path, encoding="utf-8") as fh:
        questions = [json.loads(line) for line in fh if line.strip()]
    for q in questions:
        wanted = {q["golden_chunk_id"], *q.get("alt_chunk_ids", [])}
        results = search_fn(q["question"], n_results=top)
        got = next((r for r in results if r["chunk_id"] in wanted), None)
        hits += got is not None
        mark = f"HIT @{got['rank']}" if got else "MISS"
        rank, _ = deep_dense_rank(q["question"], wanted)
        top3 = ", ".join(f"{r['metadata']['form_number']}/{r['metadata']['clause_id']}"
                         for r in results)
        print(f"  {q['id']} [{mark:<6s}] golden={q['golden_chunk_id']} "
              f"(dense rank {rank}) | top-{top}: {top3}")
    print(f"\n  {mode}: {hits}/{len(questions)} hit-rate@{top}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="?", help="a single query to inspect")
    parser.add_argument("--golden", help="known-correct chunk_id for the query")
    parser.add_argument("--golden-set", help="path to golden_set.jsonl — inspect all questions")
    parser.add_argument("--mode", choices=["dense", "fused", "both"], default="both")
    parser.add_argument("--top", type=int, default=TOP_K)
    args = parser.parse_args()

    if args.golden_set:
        mode = "dense" if args.mode == "both" else args.mode
        show_golden_set(args.golden_set, mode, args.top)
    elif args.query:
        golden = {args.golden} if args.golden else None
        show_query(args.query, golden, args.mode, args.top)
    else:
        parser.error("give a query or --golden-set")


if __name__ == "__main__":
    main()
