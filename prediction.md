# Prediction — written 2026-09-07, before any fix

Read 20 traces sampled at random (seed `20260907`) from the 140 in `traces/traffic.jsonl`.
Taxonomy in `taxonomy.md`, observation sentences in `notes.md`.

## The mode I will attack next week

**Mode 1 — "citation printed in brackets the citation checker cannot parse."**
Baseline **4 / 20 = 20%** of the sampled traces. Four times the next-largest mode, and the
only mode in the taxonomy whose fix produces a number a 20-trace sample can actually move.

## The change

One change, in the write path only: a citation normaliser applied to the model's raw output
before the trace is written, which rewrites `【SOURCE: … 】` to `[SOURCE: … ]` and folds
U+2011 non-breaking hyphens to ASCII hyphens inside the source tag. Retrieval, the prompt,
the model and its parameters stay exactly as they are.

## The number I expect

| Metric | Now (2026-09-07) | Predicted (2026-09-14) |
|---|---|---|
| Mode 1 frequency, fresh seeded sample of 20 | 4 / 20 = **20%** | **≤ 1 / 20 = 5%** |
| hit-rate@3 on `golden_set.jsonl` | 12 / 12 | **12 / 12, unchanged** |
| Non-refusal traces whose source tags parse as `[SOURCE: …]` | 13 / 17 | **≥ 16 / 17** |

Measured on a **new** week of traffic with a **new** seed, not on the 20 read this week.

## How I will be wrong

- Mode 1 still above 5% on the fresh sample.
- hit-rate@3 moves in either direction — that would mean the change did not stay in the
  write path.
- The normaliser produces a citation that resolves to a chunk_id that was never retrieved.

Any of those three and the prediction failed. I am recording it now so that next week I
cannot quietly redefine what I expected.
