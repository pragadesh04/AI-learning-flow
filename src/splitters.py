"""
splitters.py — Two chunking strategies for insurance endorsements.

Strategy A: NAIVE — fixed token-window sliding chunks (400 tokens, 50 overlap).
Strategy B: STRUCTURE-AWARE — splits on clause/section headers; keeps every
            exclusion table row attached to its table header and form number.

Both return the same shape: a list of {"text": str, "metadata": dict}.
"""

import re

import tiktoken

MAX_TOKENS = 400
OVERLAP = 50

_ENC = tiktoken.get_encoding("cl100k_base")


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _token_len(text: str) -> int:
    return len(_ENC.encode(text))


def _split_tokens(text: str, max_tokens: int = MAX_TOKENS, overlap: int = OVERLAP) -> list[str]:
    """Split *text* into token-windows of at most *max_tokens* with *overlap*."""
    tokens = _ENC.encode(text)
    windows = []
    for start in range(0, len(tokens), max_tokens - overlap):
        windows.append(_ENC.decode(tokens[start:start + max_tokens]))
        if start + max_tokens >= len(tokens):
            break  # this window already reached the end of the text
    return windows


def _make_chunk(text: str, base_meta: dict, chunk_id: str, index: int,
                strategy: str, clause_id: str) -> dict:
    """Build one chunk dict. Every chunk carries the full ingest metadata."""
    return {
        "text": text,
        "metadata": {
            **base_meta,
            "chunk_id": chunk_id,
            "chunk_index": index,
            "strategy": strategy,
            "clause_id": clause_id,
        },
    }


# ---------------------------------------------------------------------------
# Strategy A — NAIVE chunker
# ---------------------------------------------------------------------------

def naive_chunker(text: str, metadata: dict) -> list[dict]:
    """
    Fixed 400-token sliding window with 50-token overlap.
    No awareness of headers, tables, or clause boundaries.
    """
    form = metadata.get("form_number", "UNKNOWN")
    return [
        _make_chunk(window, metadata, f"{form}_naive_chunk_{i:03d}", i, "naive", "N/A")
        for i, window in enumerate(_split_tokens(text))
    ]


# ---------------------------------------------------------------------------
# Strategy B — STRUCTURE-AWARE chunker
# ---------------------------------------------------------------------------

# Header patterns that start a new chunk
_HEADER_RE = re.compile(
    r"""(?x)
    (?:^|\n)                         # start of line
    (?:
        SECTION\s+[IVXLCDM\d]+       # SECTION I, II, III ...
        | CLAUSE\s+[A-Z]{2,4}-\d+    # CLAUSE WD-1, EM-2 ...
        | EXCLUSION\s+TABLE          # EXCLUSION TABLE header
        | (?:E-\d{1,3})\s*[\|—]      # table row starting with E-NN
        | HOMEOWNERS\s+ENDORSEMENT   # document title
        | Form\s+Number:             # metadata header block
        | END\s+OF\s+ENDORSEMENT     # trailer
    )
    """,
    re.MULTILINE,
)

# An exclusion table row: | E-17 | ... |
_EXCL_ROW_RE = re.compile(r"^\|\s*E-\d{1,3}\s*\|", re.MULTILINE)

# The table header line: EXCLUSION TABLE — HO-0304 ed. 03-24
_TABLE_HEADER_RE = re.compile(
    r"EXCLUSION TABLE\s*[—-]\s*([A-Z0-9-]+\s+ed\.\s+[0-9]{2}-[0-9]{2})",
    re.IGNORECASE,
)


def _detect_clause_id(segment: str) -> str:
    """Best-effort clause ID for a segment, most specific match first."""
    if _TABLE_HEADER_RE.search(segment):
        return "EXCLUSION-TABLE"

    if _EXCL_ROW_RE.search(segment):
        codes = dict.fromkeys(re.findall(r"E-\d{1,3}", segment))
        return f"EXCLUSION-TABLE-{'-'.join(codes)}"

    clause = re.search(r"CLAUSE\s+([A-Z]{2,4}-\d+)", segment)
    if clause:
        return f"CLAUSE-{clause.group(1)}"

    section = re.search(r"SECTION\s+([IVXLCDM\d]+)", segment)
    if section:
        return f"SECTION-{section.group(1)}"

    return "PREAMBLE"


def _split_on_headers(text: str) -> list[str]:
    """Cut the document at every structural header. Each segment starts at one."""
    boundaries = sorted({0, len(text), *(m.start() for m in _HEADER_RE.finditer(text))})
    segments = (text[start:end].strip() for start, end in zip(boundaries, boundaries[1:]))
    return [seg for seg in segments if seg]


def _glue_exclusion_rows(segments: list[str]) -> list[str]:
    """
    Merge a bare exclusion row back onto the segment holding its table header,
    so a row like '| E-17 | ...' never floats away from HO-0304's table.
    """
    merged: list[str] = []
    for seg in segments:
        orphan_row = _EXCL_ROW_RE.search(seg) and not _TABLE_HEADER_RE.search(seg)
        if orphan_row and merged:
            merged[-1] += "\n" + seg
        else:
            merged.append(seg)
    return merged


def structure_aware_chunker(text: str, metadata: dict) -> list[dict]:
    """
    Splits on form/clause headers and never separates an exclusion row from
    its table header or form number.

    Every chunk is prefixed with '[FORM ed. DATE] CLAUSE-ID' so the embedding
    always sees which endorsement the text belongs to.
    """
    form = metadata.get("form_number", "UNKNOWN")
    edition = metadata.get("edition_date", "")

    segments = _glue_exclusion_rows(_split_on_headers(text))

    chunks = []
    for i, segment in enumerate(segments):
        clause_id = _detect_clause_id(segment)
        anchored = f"[{form} ed. {edition}] {clause_id}\n{segment}"
        base_id = f"{form}_sa_chunk_{i:03d}"

        if _token_len(anchored) <= MAX_TOKENS:
            chunks.append(_make_chunk(anchored, metadata, base_id, i, "structure_aware", clause_id))
            continue

        # Long segment: sub-split it, but every piece keeps the same clause_id.
        for j, part in enumerate(_split_tokens(anchored)):
            chunks.append(
                _make_chunk(part, metadata, f"{base_id}_{j:02d}", i * 100 + j,
                            "structure_aware", clause_id)
            )

    return chunks
