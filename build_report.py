#!/usr/bin/env python3
"""
build_report.py — Master runner for Week 3 Practical Task Set D.

Steps:
  1. Ingest the 6 endorsements into both collections (base wording NOT re-indexed)
  2. Run the 8 known-answer questions search-only against both strategies
  3. Run the metadata filter demo
  4. Generate 3 cited answers
  5. Ask 3 out-of-corpus questions that must be refused
  6. Write report.md — generated evidence, with writeup.md spliced in

Usage:
    python build_report.py
"""

import os
import sys
import time
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()  # pick up GROQ_API_KEY from .env before anything needs it

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "src"))

from eval_harness import (
    FILTER_DEMO_QUERY,
    QUESTIONS,
    STRATEGIES,
    questions_by_id,
    run_evaluation,
    run_filter_demo,
)
from answerer import MODEL, answer_questions
from indexer import EMBEDDING_MODEL, ingest_all

WRITEUP_PATH = os.path.join(HERE, "writeup.md")
REPORT_PATH = os.path.join(HERE, "report.md")

# The 3 cited answers reuse questions from the known-answer set, so every
# citation can be checked against a form_number and clause written down first.
ANSWERABLE_IDS = ["Q1", "Q5", "Q8"]

# Real claims-system questions whose answers live nowhere in the 6 endorsements.
UNANSWERABLE_QUESTIONS = [
    "What is the reserve-setting threshold for claim CLM-2024-88431 "
    "and what adjuster was assigned?",
    "What was the payout amount on claim number CLM-2023-44201 for roof "
    "damage at 512 Elm Street, and was subrogation pursued against the contractor?",
    "What is the underwriting guideline for maximum insured value on a "
    "coastal homeowners policy in flood zone AE under the company's internal "
    "risk appetite framework?",
]


# ---------------------------------------------------------------------------
# Small markdown helpers
# ---------------------------------------------------------------------------

def _row(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |\n"


def result_table(results: list[dict]) -> str:
    """The rank/score/chunk_id table — used for every result list in the report."""
    headers = ["Rank", "Score", "chunk_id", "form_number", "clause_id"]
    md = _row(headers) + _row(["---"] * len(headers))
    for r in results:
        md += _row([
            str(r["rank"]),
            f"{r['score']:.4f}",
            f"`{r['chunk_id']}`",
            r["metadata"].get("form_number", "?"),
            r["metadata"].get("clause_id", "?"),
        ])
    return md


def read_analysis() -> str:
    """
    The hand-written sections (chunking decision, miss diagnoses, bonus, diff).
    They live in writeup.md so re-running this script regenerates the evidence
    without ever overwriting the reasoning.
    """
    if not os.path.exists(WRITEUP_PATH):
        return "> writeup.md is missing — write the chunking decision there.\n\n"
    with open(WRITEUP_PATH, encoding="utf-8") as fh:
        text = fh.read()
    # Drop the editing note at the top; it belongs in writeup.md only.
    _, marker, body = text.partition("## ")
    return ((marker + body) if marker else text).strip() + "\n\n"


# ---------------------------------------------------------------------------
# report.md sections
# ---------------------------------------------------------------------------

def header_section(ingest_stats: dict) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    md = f"""# Week 3 Practical — Task Set D: Results

**Domain:** Insurance Claims — Endorsement RAG  
**Module:** M2 — Retrieval & RAG  
**Generated:** {now}  
**Model:** {MODEL} via Groq API  
**Embeddings:** sentence-transformers/{EMBEDDING_MODEL} (local)  
**Vector Store:** ChromaDB (persistent, local)

> **Scope note:** Only the 6 new endorsements (HO-0304 through HO-0309) were
> indexed. The base homeowners wording library was NOT re-indexed. Both
> chunking strategy collections were built fresh from these 6 files only.

---

## Ingest Summary

"""
    md += _row(["Stat", "Value"]) + _row(["---", "---"])
    md += _row(["Files processed", str(ingest_stats["files_processed"])])
    for strategy, count in ingest_stats["chunks"].items():
        md += _row([f"{strategy} chunks created", str(count)])
    md += _row(["Failed files (no metadata)", str(len(ingest_stats["failed_files"]))])
    md += """
**Metadata fields on every chunk:** `source_file`, `form_number`, `policy_line`,
`edition_date`, `chunk_id`, `clause_id`, `strategy`, `chunk_index`

A chunk with no `source_file` is a failed ingest. Metadata comes from the
filename (`HO-0304_03-24.txt`), so a file that cannot be parsed is skipped and
counted as a failure rather than indexed without provenance.

---

"""
    return md


def questions_section() -> str:
    md = """## The 8 Known-Answer Questions

> Questions were written BEFORE running any retrieval, directly from the
> endorsement text files. Answers verified by form_number and clause.

"""
    headers = ["#", "Question", "Expected Form", "Expected Clause / Code"]
    md += _row(headers) + _row(["---"] * len(headers))
    for q in QUESTIONS:
        md += _row([q["id"], q["question"], q["expected_form"], q["expected_clause"]])
    return md + "\n---\n\n"


def hit_rate_section(evaluation: dict) -> str:
    scores, total = evaluation["scores"], evaluation["total"]

    md = "## Hit-in-Top-5: Both Chunking Strategies\n\n"
    headers = ["Q#", "Question (short)", "Expected Form"]
    for strategy in STRATEGIES:
        headers += [f"{strategy} hit?", f"{strategy} rank"]
    md += _row(headers) + _row(["---"] * len(headers))

    for record in evaluation["records"]:
        cells = [record["id"], record["question"][:55] + "…", record["expected_form"]]
        for strategy in STRATEGIES:
            rank = record[f"rank_{strategy}"]
            cells += [
                "✅" if record[f"hit_{strategy}"] else "❌",
                str(rank) if rank else "—",
            ]
        md += _row(cells)

    totals = ["**TOTAL**", "", ""]
    for strategy in STRATEGIES:
        totals += [f"**{scores[strategy]}/{total}**", ""]
    md += _row(totals) + "\n"

    for strategy in STRATEGIES:
        md += f"**{strategy} chunker:** {scores[strategy]}/{total} in top-5  \n"
    return md + "\n---\n\n"


def filter_section(filter_demo: dict) -> str:
    def top1(results: list[dict]) -> str:
        if not results:
            return "— (no results)"
        top = results[0]
        return f"`{top['chunk_id']}` (form: {top['metadata'].get('form_number', '—')})"

    return f"""## Metadata Filter Demo

**Query:** `{FILTER_DEMO_QUERY}`  
**Filter applied:** `policy_line = "homeowners"`  

### Unfiltered Results (top-5)

{result_table(filter_demo["unfiltered"])}
### Filtered Results (policy_line = "homeowners")

{result_table(filter_demo["filtered"])}
**Top-1 unfiltered:** {top1(filter_demo["unfiltered"])}  
**Top-1 filtered:**   {top1(filter_demo["filtered"])}

The `policy_line` filter restricts results to homeowners-line endorsements.
All 6 indexed endorsements are on the homeowners line, so this proves the
provenance constraint works end-to-end; in a multi-line corpus (auto,
commercial) the same filter is what removes cross-line noise.

---

"""


def answers_section(answers: list[dict]) -> str:
    md = "## Cited Answers — 3 Answerable Questions\n\n"
    for i, answer in enumerate(answers, start=1):
        chunk_ids = ", ".join(f"`{c}`" for c in answer["hits_used"])
        md += f"""### Answer {i}

**Q:** {answer['question']}

**Known-correct source:** {answer['expected_form']} / {answer['expected_clause']}

**Answer:**

```
{answer['answer']}
```

**Chunks retrieved:** {chunk_ids}

---

"""
    return md


def refusals_section(refusals: list[dict]) -> str:
    md = "## Refusal Transcripts — 3 Out-of-Corpus Questions\n\n"
    for i, refusal in enumerate(refusals, start=1):
        label = (
            "✅ CORRECTLY REFUSED" if refusal["is_refusal"]
            else "❌ HALLUCINATED (failure)"
        )
        md += f"""### Refusal {i} — {label}

**Q:** {refusal['question']}

**Model response:**

```
{refusal['answer']}
```

---

"""
    return md


def search_dump_section(evaluation: dict) -> str:
    """
    Full top-5 for all 8 questions under both strategies. Reuses the results
    the evaluation already collected instead of searching all over again.
    """
    md = "## Search-Only Dump — All 8 Questions, Both Strategies\n\n"
    for strategy in STRATEGIES:
        md += f"### Strategy: {strategy}\n\n"
        for record in evaluation["records"]:
            md += f"**{record['id']}:** {record['question']}\n\n"
            md += result_table(record[f"results_{strategy}"]) + "\n"
        md += "---\n\n"
    return md


def build_results_md(ingest_stats, evaluation, filter_demo, answers, refusals) -> str:
    return (
        header_section(ingest_stats)
        + questions_section()
        + hit_rate_section(evaluation)
        + filter_section(filter_demo)
        + answers_section(answers)
        + refusals_section(refusals)
        + read_analysis()
        + search_dump_section(evaluation)
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    started = time.perf_counter()

    print("─" * 60)
    print("Week 3 Practical — Task Set D")
    print("Insurance Claims RAG: Endorsement Chunking Evaluation")
    print("─" * 60)

    print("\n[1/5] Ingesting endorsements (base wording NOT re-indexed)...")
    ingest_stats = ingest_all(reset=True)

    print(f"\n[2/5] Running the {len(QUESTIONS)} known-answer questions (search-only)...")
    evaluation = run_evaluation(verbose=True)

    print("\n[3/5] Running the metadata filter demo...")
    filter_demo = run_filter_demo(verbose=True)

    print(f"\n[4/5] Generating {len(ANSWERABLE_IDS)} cited answers...")
    answers = answer_questions(questions_by_id(ANSWERABLE_IDS), verbose=True)

    print(f"\n[5/5] Asking {len(UNANSWERABLE_QUESTIONS)} out-of-corpus questions "
          "(these must be refused)...")
    refusals = answer_questions(
        [{"question": q} for q in UNANSWERABLE_QUESTIONS], verbose=True
    )

    print("\nWriting report.md...")
    with open(REPORT_PATH, "w", encoding="utf-8") as fh:
        fh.write(
            build_results_md(ingest_stats, evaluation, filter_demo, answers, refusals)
        )

    refused = sum(r["is_refusal"] for r in refusals)
    print("\n" + "─" * 60)
    print("FINAL SCORES")
    for strategy, score in evaluation["scores"].items():
        print(f"  {strategy:>17s} chunker: {score}/{evaluation['total']}")
    print(f"  {'correctly refused':>17s}: {refused}/{len(refusals)}")
    print("─" * 60)
    print(f"  ✓ report.md written to: {REPORT_PATH}")
    print(f"    finished in {time.perf_counter() - started:.1f}s\n")


if __name__ == "__main__":
    main()
