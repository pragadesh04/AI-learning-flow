"""
indexer.py — Ingest the 6 endorsements into TWO ChromaDB collections:
  • 'endorsements_naive'           — Strategy A chunks
  • 'endorsements_structure_aware' — Strategy B chunks

Every chunk carries: source_file, form_number, policy_line, edition_date,
chunk_id, clause_id, strategy, chunk_index.

NOTE: Only the 6 new endorsements are indexed. The base wording library is
NOT re-indexed (per the assignment constraint — see report.md).
"""

import os
import re
import sys
from functools import lru_cache

import chromadb
from chromadb.utils import embedding_functions

sys.path.insert(0, os.path.dirname(__file__))
from splitters import naive_chunker, structure_aware_chunker

HERE = os.path.dirname(os.path.abspath(__file__))
ENDORSEMENTS_DIR = os.path.join(HERE, "..", "endorsements")
CHROMA_DB_PATH = os.path.join(HERE, "..", "chroma_db")

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# One collection and one chunker per strategy — add a third here and the whole
# pipeline picks it up.
COLLECTIONS = {
    "naive": "endorsements_naive",
    "structure_aware": "endorsements_structure_aware",
}
CHUNKERS = {
    "naive": naive_chunker,
    "structure_aware": structure_aware_chunker,
}


# ---------------------------------------------------------------------------
# Metadata straight off the filename: "HO-0304_03-24.txt"
# ---------------------------------------------------------------------------

_FILENAME_RE = re.compile(
    r"^(?P<form>(?P<line>[A-Z]{2})-\d{4})_(?P<edition>\d{2}-\d{2})\.txt$"
)
POLICY_LINES = {"HO": "homeowners"}


def parse_metadata(filename: str) -> dict | None:
    """
    Turn 'HO-0304_03-24.txt' into the four fields every chunk must carry.
    Returns None if the filename doesn't follow FORM_EDITION.txt — that file
    is a failed ingest rather than a chunk with missing provenance.
    """
    match = _FILENAME_RE.match(filename)
    if not match:
        return None
    return {
        "source_file": filename,
        "form_number": match["form"],
        "edition_date": match["edition"],
        "policy_line": POLICY_LINES.get(match["line"], "unknown"),
    }


# ---------------------------------------------------------------------------
# ChromaDB handles — cached, because loading the embedding model is slow
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def get_embedding_fn():
    """Local sentence-transformers embeddings. No API key needed."""
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )


@lru_cache(maxsize=1)
def get_client():
    return chromadb.PersistentClient(path=CHROMA_DB_PATH)


def get_collection(strategy: str):
    """Open (creating if needed) the collection for one chunking strategy."""
    return get_client().get_or_create_collection(
        name=COLLECTIONS[strategy],
        embedding_function=get_embedding_fn(),
        metadata={"hnsw:space": "cosine"},
    )


# ---------------------------------------------------------------------------
# Ingest
# ---------------------------------------------------------------------------

def ingest_all(reset: bool = True) -> dict:
    """
    Chunk each endorsement with both strategies and index each set into its
    own collection.

    Args:
        reset: drop the collections first, so a re-run is a clean run.

    Returns:
        stats dict used by the report.md write-up.
    """
    if reset:
        for name in COLLECTIONS.values():
            try:
                get_client().delete_collection(name)
                print(f"  dropped existing collection: {name}")
            except Exception:
                pass  # first run — nothing to drop

    collections = {strategy: get_collection(strategy) for strategy in CHUNKERS}
    stats = {
        "files_processed": 0,
        "failed_files": [],
        "chunks": {strategy: 0 for strategy in CHUNKERS},
    }

    for filename in sorted(os.listdir(ENDORSEMENTS_DIR)):
        if not filename.endswith(".txt"):
            continue

        base_meta = parse_metadata(filename)
        if base_meta is None:
            print(f"  ! {filename} is not named FORM_EDITION.txt — skipping.")
            stats["failed_files"].append(filename)
            continue

        with open(os.path.join(ENDORSEMENTS_DIR, filename), encoding="utf-8") as fh:
            text = fh.read()

        counts = {}
        for strategy, chunker in CHUNKERS.items():
            chunks = chunker(text, base_meta)
            _upsert(collections[strategy], chunks)
            stats["chunks"][strategy] += len(chunks)
            counts[strategy] = len(chunks)

        stats["files_processed"] += 1
        summary = "  ".join(f"{s}={n}" for s, n in counts.items())
        print(f"  {filename:<20s} {summary} chunks")

    totals = ", ".join(f"{n} {s}" for s, n in stats["chunks"].items())
    print(f"\n  ✓ ingest complete: {stats['files_processed']} files, {totals}")
    if stats["failed_files"]:
        print(f"  ! {len(stats['failed_files'])} file(s) failed to ingest")
    return stats


def _upsert(collection, chunks: list[dict]) -> None:
    """Write chunks into a collection. chunk_id doubles as the ChromaDB id."""
    if not chunks:
        return
    collection.upsert(
        ids=[c["metadata"]["chunk_id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[c["metadata"] for c in chunks],
    )


def resolve_chunk(chunk_id: str, strategy: str = "structure_aware") -> dict | None:
    """Look a chunk_id back up — this is what makes a citation checkable."""
    result = get_collection(strategy).get(
        ids=[chunk_id], include=["documents", "metadatas"]
    )
    if not result["ids"]:
        return None
    return {
        "chunk_id": chunk_id,
        "text": result["documents"][0],
        "metadata": result["metadatas"][0],
    }


if __name__ == "__main__":
    print("Ingesting the endorsements (base wording NOT re-indexed)...\n")
    ingest_all(reset=True)
