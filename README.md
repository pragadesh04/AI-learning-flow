# Insurance Endorsement RAG — A Chunking Bake-Off

*Weeks 3–4 Practicals · Task Set D · Module M2 — Retrieval & RAG*

Six homeowners policy endorsements go in. Two chunking strategies index them
side by side, eight known-answer questions are fired at both, and the run
writes up which strategy actually found the answer — and where each one failed.

**Week 4 put that retriever on trial.** A 12-question golden set with
known-correct chunk_ids (`golden_set.jsonl`) measured hit-rate@3, every
failure was labelled R / G / Not-In-Corpus through an inspection view, and
exactly ONE retrieval change — BM25 + RRF rank fusion, k=60
(`src/hybrid.py`) — took **hit-rate@3 from 11/12 to 12/12** at unchanged
p50 latency. The MMR bonus was measured and rejected (it pays hits for
variety). `ask.py` now retrieves through the fused path.

The point of the project is not the chatbot. It is the evidence: `report.md`
(Week 3) and `results.md` (Week 4) are generated scorecards, not claims.

---

## The two strategies under test

| | Strategy A — *naive* | Strategy B — *structure-aware* |
|---|---|---|
| Split on | Fixed 400-token window, 50-token overlap | Form/clause headers (`SECTION`, `CLAUSE`, `EXCLUSION TABLE`, `E-NN`) |
| Knows about tables | No | Yes — never orphans an exclusion row from its table header |
| Embedding text | Raw chunk | Prefixed with `[form_number ed. edition_date] clause_id` |
| Chroma collection | `endorsements_naive` | `endorsements_structure_aware` |

Both are indexed on every run, so every question is scored against both.

---

## Quickstart

**Requirements:** Python 3.10+ and a free Groq API key
([console.groq.com/keys](https://console.groq.com/keys)).

```bash
# 1 — clone and enter the project
git clone https://github.com/pragadesh04/AI-learning-flow.git
cd AI-learning-flow

# 2 — isolated environment
python -m venv venv
venv\Scripts\activate         # Windows
# source venv/bin/activate     # macOS / Linux

# 3 — dependencies
pip install -r requirements.txt

# 4 — API key
cp .env.example .env          # then edit .env:
#   GROQ_API_KEY=gsk_your_actual_key_here
```

---

## Running it

**Build the vector index** — parses the 6 endorsements, chunks each one twice,
and writes both collections into a local `chroma_db/` (never committed):

```bash
python src/indexer.py
```

**Produce the deliverable** — the whole pipeline end to end:

```bash
python build_report.py
```

**Ask it something yourself** — an interactive CLI with citations, retrieving
through the Week-4 hybrid path (dense + BM25, RRF-fused):

```bash
python ask.py
```

**Week 4 — measure retrieval, label failures, regenerate `results.md`:**

```bash
python week4_eval.py                     # full run: baseline → labels → one change → after → MMR
python week4_eval.py --skip-generation   # same numbers, no API call (skips R/G transcripts)
```

**Inspect a single query** — ranks, scores, dense/BM25 provenance, and where
the known-correct chunk actually sits:

```bash
python inspect_retrieval.py "effective date of HO-0305 ed. 03-24" --golden HO-0305_sa_chunk_010
python inspect_retrieval.py --golden-set golden_set.jsonl --mode fused
```

### What `build_report.py` actually does

1. Ingests the 6 endorsements into both collections (base wording is *not* touched)
2. Fires the 8 known-answer questions at both strategies — retrieval only, scored as hit-in-top-5
3. Runs the metadata filter demo (same query, with and without `policy_line="homeowners"`)
4. Generates 3 fully cited answers
5. Asks 3 out-of-corpus questions that *must* be refused
6. Writes `report.md`, splicing your hand-written sections in from `writeup.md`

Re-running is safe and idempotent: the index is rebuilt from scratch and
`writeup.md` is only ever read, never written.

---

## Where things live

```
├── endorsements/               # 6 synthetic homeowners endorsements
│   ├── HO-0304_03-24.txt       # Water damage + supply line coverage
│   ├── HO-0305_03-24.txt       # Named storm deductible
│   ├── HO-0306_04-24.txt       # Mold and fungi exclusion
│   ├── HO-0307_04-24.txt       # Scheduled personal property
│   ├── HO-0308_05-24.txt       # Earth movement exclusion (broadened)
│   └── HO-0309_05-24.txt       # Business pursuits exclusion
├── src/
│   ├── splitters.py            # The two chunkers
│   ├── indexer.py              # Filename → metadata → ChromaDB
│   ├── retriever.py            # Vector search + metadata filtering (the dense path)
│   ├── hybrid.py               # Week 4: BM25 + RRF fusion — the one retrieval change
│   ├── answerer.py             # Groq generation + the refusal rule
│   └── eval_harness.py         # Week 3: the 8 questions and how they're scored
├── build_report.py             # Week 3 pipeline end to end, writes report.md
├── week4_eval.py               # Week 4 pipeline end to end, writes results.md
├── inspect_retrieval.py        # Inspection view — evidence behind every R/G label
├── golden_set.jsonl            # Week 4: 12 questions tagged with known-correct chunk_ids
├── ask.py                      # Interactive CLI (fused retrieval)
├── writeup.md                  # ✍️  Your analysis — edit this one
├── report.md                   # 🤖  Generated (Week 3) — don't hand-edit
├── results.md                  # 🤖  Generated (Week 4) — don't hand-edit
├── task_brief.md               # The Week 3 assignment
├── requirements.txt            # Pinned dependencies
└── .env.example                # API key template
```

> **Which file do I write in?** `writeup.md`. Everything in `report.md` is
> regenerated on each run, and your prose is spliced into it verbatim — so
> edits made directly to `report.md` are silently lost on the next run.

`chroma_db/`, `venv/`, `.env`, and `__pycache__/` are git-ignored and rebuilt
locally.

---

## Stack

| Piece | Choice |
|---|---|
| Generation | `openai/gpt-oss-120b` via the Groq API (OpenAI-compatible client) |
| Embeddings | `all-MiniLM-L6-v2` — sentence-transformers, runs locally |
| Vector store | ChromaDB, persistent, on disk |
| Tokenizer | tiktoken (chunk budgeting) |
| Python | 3.10+ |

No embedding calls leave the machine; only generation hits the network.

---

## Design notes

**Metadata comes from the filename.** `HO-0304_03-24.txt` yields
`form_number`, `edition_date`, `policy_line` and `source_file` with no manual
mapping, so dropping a new endorsement into `endorsements/` is the entire
onboarding process. A file that doesn't match the pattern is reported as a
*failed ingest* rather than indexed with missing provenance — silent
half-indexed documents are worse than a loud failure.

Every chunk carries:

| Field | Example |
|---|---|
| `source_file` | `HO-0304_03-24.txt` |
| `form_number` | `HO-0304` |
| `edition_date` | `03-24` |
| `policy_line` | `homeowners` |
| `clause_id` | `EXCLUSION-TABLE-E-17` |
| `chunk_id` | unique and resolvable back to its text |
| `strategy` | `naive` \| `structure_aware` |
| `chunk_index` | position within the document |

**Refusal is a hard rule, not a preference.** The system prompt requires the
model to emit a `REFUSAL:` message when the answer isn't in the retrieved
context. "Use your best judgment" is explicitly forbidden — in a claims
setting, a confident guess about coverage is the failure mode worth designing
against, and the pipeline tests for it with 3 deliberately out-of-corpus
questions.

**Adding a third strategy** is two entries: a chunker in `splitters.py`, then
a line each in `COLLECTIONS` and `CHUNKERS` in `indexer.py`. Ingest,
evaluation, and the report all iterate over those dicts.

---

## Scope constraint

Only the 6 new endorsements are indexed. The base wording library is
deliberately **not** re-indexed, per the assignment. Anything outside those
six documents — claim records, adjuster assignments, internal underwriting
guidelines — is therefore out of corpus by design, and the refusal test uses
exactly that kind of question.
