"""
eval_harness.py — Search-only evaluation harness for Week 3 Practical Task Set D.

Runs the 8 known-answer questions against every chunking strategy and records
hit-in-top-5 per question. No generation here — retrieval is measured alone,
so the number reflects the chunker and nothing else.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from indexer import CHUNKERS
from retriever import format_results, hit_in_top5, metadata_filter_demo

# Whatever strategies ingest knows about, we evaluate. Same 8 questions for all.
STRATEGIES = list(CHUNKERS)

# ---------------------------------------------------------------------------
# The 8 known-answer questions.
# Written BEFORE running any retrieval, straight from the endorsement text —
# otherwise the hit-rate would be measuring the question-writing, not the chunker.
# ---------------------------------------------------------------------------

QUESTIONS = [
    {
        "id": "Q1",
        "question": (
            "Does exclusion E-17 apply to water damage caused by a burst supply "
            "line under endorsement HO-0304 ed. 03-24?"
        ),
        "expected_form": "HO-0304",
        "expected_clause": "E-17",           # the exclusion table row
        "expected_answer_fragment": "E-17",  # must appear in the retrieved text
        "note": "Table row — E-17 explicitly confirms coverage is NOT withheld.",
    },
    {
        "id": "Q2",
        "question": "What is the effective date of endorsement HO-0305 ed. 03-24?",
        "expected_form": "HO-0305",
        "expected_clause": "SECTION-IV",
        "expected_answer_fragment": "March 15, 2024",
        "note": "Header metadata — effective date March 15, 2024.",
    },
    {
        "id": "Q3",
        "question": "Does exclusion E-22 in HO-0306 ed. 04-24 cover mold damage?",
        "expected_form": "HO-0306",
        "expected_clause": "EXCLUSION-TABLE",
        "expected_answer_fragment": "E-22",
        "note": "Table row — E-22 excludes general mold damage.",
    },
    {
        "id": "Q4",
        "question": "What policy line does endorsement HO-0307 ed. 04-24 modify?",
        "expected_form": "HO-0307",
        "expected_clause": "PREAMBLE",
        "expected_answer_fragment": "homeowners",
        "note": "Preamble header — policy_line is homeowners.",
    },
    {
        "id": "Q5",
        "question": (
            "Under endorsement HO-0308 ed. 05-24, does exclusion E-31 apply "
            "to damage caused by earth movement?"
        ),
        "expected_form": "HO-0308",
        "expected_clause": "EXCLUSION-TABLE",
        "expected_answer_fragment": "E-31",
        "note": "Table row — E-31 excludes all forms of earth movement.",
    },
    {
        "id": "Q6",
        "question": (
            "What is the Named Storm deductible amount or formula under "
            "HO-0305 ed. 03-24?"
        ),
        "expected_form": "HO-0305",
        "expected_clause": "CLAUSE-NS-2",
        "expected_answer_fragment": "2%",
        "note": "CLAUSE NS-2 — $5,000 or 2% of Coverage A, whichever greater.",
    },
    {
        "id": "Q7",
        "question": (
            "Does endorsement HO-0309 ed. 05-24 contain a business pursuits "
            "exclusion, and if so, what is its exclusion code?"
        ),
        "expected_form": "HO-0309",
        "expected_clause": "EXCLUSION-TABLE",
        "expected_answer_fragment": "E-19",
        "note": "Table row — E-19 is the business pursuits exclusion in HO-0309.",
    },
    {
        "id": "Q8",
        "question": (
            "Under HO-0304 ed. 03-24, what clause defines 'sudden and accidental' "
            "and what is the time limit for continuous leakage before coverage is lost?"
        ),
        "expected_form": "HO-0304",
        "expected_clause": "CLAUSE-WD-1",
        "expected_answer_fragment": "14",
        "note": "CLAUSE WD-1 — sudden and accidental; 14-day seepage limit.",
    },
]

FILTER_DEMO_QUERY = "Does exclusion E-31 apply to earth movement damage?"


def questions_by_id(ids: list[str]) -> list[dict]:
    """Pick questions out of the set above, so nothing gets re-typed."""
    lookup = {q["id"]: q for q in QUESTIONS}
    return [lookup[qid] for qid in ids]


# ---------------------------------------------------------------------------
# Run evaluation
# ---------------------------------------------------------------------------

def run_evaluation(verbose: bool = True) -> dict:
    """
    Run all 8 questions against every strategy, search-only.

    Returns:
        dict with per-question records, per-strategy scores, and the total.
    """
    records = []
    for q in QUESTIONS:
        record = {key: q[key] for key in ("id", "question", "expected_form",
                                          "expected_clause", "note")}
        for strategy in STRATEGIES:
            result = hit_in_top5(
                q["question"],
                q["expected_form"],
                q["expected_answer_fragment"],
                strategy=strategy,
                n_results=5,
            )
            record[f"hit_{strategy}"] = result["hit"]
            record[f"rank_{strategy}"] = result["rank"]
            record[f"results_{strategy}"] = result["results"]

            if verbose:
                mark = "✓" if result["hit"] else "✗"
                outcome = f"rank {result['rank']}" if result["hit"] else "not in top-5"
                print(
                    f"  {mark} [{strategy:>16s}] {q['id']}: {outcome:<13s} | "
                    f"needs={q['expected_answer_fragment']!r}"
                )
        records.append(record)

    scores = {s: sum(r[f"hit_{s}"] for r in records) for s in STRATEGIES}

    if verbose:
        print("\n" + "─" * 50)
        for strategy, score in scores.items():
            print(f"  {strategy:>16s}: {score}/{len(QUESTIONS)}")
        print("─" * 50)

    return {"records": records, "scores": scores, "total": len(QUESTIONS)}


def run_filter_demo(verbose: bool = True) -> dict:
    """Run the metadata filter demo query and return both result lists."""
    demo = metadata_filter_demo(
        FILTER_DEMO_QUERY,
        policy_line="homeowners",
        strategy="structure_aware",
        n_results=5,
    )
    if verbose:
        print(f"\nFilter demo query: '{FILTER_DEMO_QUERY}'")
        print("\n--- UNFILTERED (top-5) ---")
        print(format_results(demo["unfiltered"]))
        print('\n--- FILTERED: policy_line="homeowners" (top-5) ---')
        print(format_results(demo["filtered"]))
    return demo


if __name__ == "__main__":
    print("Running evaluation harness...\n")
    run_evaluation(verbose=True)
    print("\nRunning metadata filter demo...\n")
    run_filter_demo(verbose=True)
