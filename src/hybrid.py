"""
hybrid.py — Week 4's single retrieval change: BM25 + RRF rank fusion (k=60).

The Week-3 dense path (retriever.search) is untouched. This module adds a
lexical BM25 ranking over the same collection and fuses the two lists with
Reciprocal Rank Fusion. RRF fuses RANKS, never raw scores — BM25 scores and
cosine similarities are not on the same scale and never were.

Why BM25 and not a cross-encoder: the Week-4 failure tally (results.md) is
dominated by R-failures on queries carrying exact tokens — exclusion codes
(E-17) and form numbers (HO-0304 ed. 03-24) — that the dense embedding
refuses to weight. A reranker can only reorder the dense candidate list;
BM25 can put a chunk on the table that dense retrieval never surfaced.
"""

import math
import os
import re
import sys
from collections import Counter
from functools import lru_cache

sys.path.insert(0, os.path.dirname(__file__))
from indexer import get_collection
from retriever import search

RRF_K = 60          # the standard RRF constant, per the task spec
CANDIDATES = 25     # depth of each ranked list going into the fusion

# 'e-17', 'ho-0304' and '03-24' survive as single tokens instead of being
# shredded into 'e' + '17' — the whole point of adding a lexical channel.
_TOKEN_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")

_K1, _B = 1.5, 0.75


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


class _BM25:
    """Plain Okapi BM25. Over 72 documents a dependency weighs more than the math."""

    def __init__(self, tokenized_docs: list[list[str]]):
        self.doc_lens = [len(d) for d in tokenized_docs]
        self.avgdl = sum(self.doc_lens) / len(self.doc_lens)
        self.tfs = [Counter(d) for d in tokenized_docs]
        df = Counter(t for tf in self.tfs for t in tf)
        n = len(tokenized_docs)
        self.idf = {t: math.log((n - c + 0.5) / (c + 0.5) + 1) for t, c in df.items()}

    def scores(self, query_tokens: list[str]) -> list[float]:
        out = []
        for tf, dl in zip(self.tfs, self.doc_lens):
            norm = _K1 * (1 - _B + _B * dl / self.avgdl)
            out.append(sum(
                self.idf[t] * tf[t] * (_K1 + 1) / (tf[t] + norm)
                for t in query_tokens if t in tf
            ))
        return out


@lru_cache(maxsize=4)
def _corpus(strategy: str = "structure_aware"):
    """
    Every chunk of one collection plus a BM25 index over it. Cached per process;
    after re-ingesting in the same process, call _corpus.cache_clear().
    """
    data = get_collection(strategy).get(include=["documents", "metadatas"])
    ids, docs, metas = data["ids"], data["documents"], data["metadatas"]
    return ids, docs, metas, _BM25([_tokenize(d) for d in docs])


def bm25_search(query: str, strategy: str = "structure_aware",
                n_results: int = CANDIDATES) -> list[str]:
    """Chunk_ids ranked by BM25. Zero-score documents carry no lexical signal and are dropped."""
    ids, _, _, bm25 = _corpus(strategy)
    scored = bm25.scores(_tokenize(query))
    order = sorted(range(len(ids)), key=lambda i: (-scored[i], ids[i]))
    return [ids[i] for i in order[:n_results] if scored[i] > 0]


def fused_search(query: str, strategy: str = "structure_aware", n_results: int = 5,
                 k: int = RRF_K, candidates: int = CANDIDATES) -> list[dict]:
    """
    Dense top-25 and BM25 top-25, fused by RRF: score(c) = Σ 1/(k + rank).

    Rows are drop-in replacements for retriever.search() results; dense_rank
    and bm25_rank record which channel surfaced each chunk, for the
    inspection view.
    """
    dense = search(query, strategy=strategy, n_results=candidates)
    lexical = bm25_search(query, strategy=strategy, n_results=candidates)

    dense_rank = {r["chunk_id"]: r["rank"] for r in dense}
    bm25_rank = {cid: i for i, cid in enumerate(lexical, start=1)}

    rrf = {
        cid: sum(1 / (k + rank)
                 for rank in (dense_rank.get(cid), bm25_rank.get(cid))
                 if rank is not None)
        for cid in dense_rank.keys() | bm25_rank.keys()
    }

    ids, docs, metas, _ = _corpus(strategy)
    by_id = {cid: (doc, meta) for cid, doc, meta in zip(ids, docs, metas)}

    ranked = sorted(rrf, key=lambda c: (-rrf[c], dense_rank.get(c, 10 ** 6), c))
    return [
        {
            "rank": i,
            "chunk_id": cid,
            "score": round(rrf[cid], 6),
            "text": by_id[cid][0],
            "metadata": by_id[cid][1],
            "dense_rank": dense_rank.get(cid),
            "bm25_rank": bm25_rank.get(cid),
        }
        for i, cid in enumerate(ranked[:n_results], start=1)
    ]
