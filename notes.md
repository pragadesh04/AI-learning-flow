# Week 5 — reading notes

Everything the taxonomy rests on: how the sample was drawn, what each of the 20 traces
actually did, the replay evidence, the redaction confirmation, and the dated prediction.

---

## 1. The seeded sample

```
population : 140 traces in traces/traffic.jsonl
seed       : 20260907
n          : 20
rule       : random.Random(seed).sample(sorted(trace_ids), n)
```

Sorting the population before the draw makes the selection independent of the order lines
were written to the log, which matters because the simulator answers on a worker pool and
the file is sorted by timestamp afterwards. The draw is reproducible with:

```bash
python week5_analysis.py sample --seed 20260907 --n 20
```

and is stored, seed and all, in `traces/sample_seed20260907.json`.

The 20 trace_ids:

```
tr_20260831T1225_0004   tr_20260905T0939_0057
tr_20260831T1556_0009   tr_20260905T1256_0060
tr_20260901T1148_0015   tr_20260905T1506_0062
tr_20260902T1647_0031   tr_20260905T1633_0064
tr_20260902T1719_0032   tr_20260906T0853_0066
tr_20260903T1540_0043   tr_20260906T1708_0074
tr_20260904T1244_0049   tr_20260908T0959_0090
tr_20260904T1606_0054   tr_20260908T1518_0096
tr_20260909T1208_0106   tr_20260911T1220_0130
tr_20260909T1719_0113   tr_20260911T1659_0134
```

These are not the demo claims and not the ones I remembered breaking. Two of them are
questions the app handles well and three are questions nobody would put in a demo.

---

## 2. Open coding — one observation sentence per trace

Written while reading, before any clustering, describing what the trace did rather than why.
**No code was changed between reading the first trace and the last.** The trace log was
already closed when reading started, so nothing read here describes a different app.

| # | trace_id | What I saw |
|---|---|---|
| 1 | `tr_20260831T1225_0004` | The answer gave fourteen consecutive days and quoted the WD-1 wording, and wrapped its source tag in `【 】` instead of the square brackets most other answers used. |
| 2 | `tr_20260831T1556_0009` | The answer named E-14 ground water intrusion correctly, but opened with "The loss is covered by exclusion E-14", so the first four words say covered on a claim that row denies. |
| 3 | `tr_20260901T1148_0015` | Five HO-0305 chunks came back, the worked $300,000 example sat at rank 1, and the answer was $6,000 with one square-bracket citation. |
| 4 | `tr_20260902T1647_0031` | The answer said no to air quality testing and pointed at both MF-3 and the E-25 table row; the chunk ranked first carried the clause label CLAUSE-WD-1 while belonging to HO-0306, and the answer did not cite it. |
| 5 | `tr_20260902T1719_0032` | The answer said the $10,000 sublimit is part of Coverage A and cited MF-4, which is what MF-4 says. |
| 6 | `tr_20260903T1540_0043` | The answer gave 25% of schedule value and 30 days from purchase, and again wrapped the source tag in `【 】`. |
| 7 | `tr_20260904T1244_0049` | The assistant refused, and the five retrieved chunks were all HO-0307 clause text with no exclusion table among them, although that form's table carries an E-32 row for government seizure. |
| 8 | `tr_20260904T1606_0054` | The answer said mining subsidence is excluded and quoted the man-made earth movement row, but never printed the code E-32. |
| 9 | `tr_20260905T0939_0057` | The question was settlement versus construction defect; the answer said the Company's engineering report controls the determination of the cause of loss, while EM-4 makes it controlling only on whether earth movement contributed. |
| 10 | `tr_20260905T1256_0060` | The answer gave $2,500 and added per occurrence and per policy year, both of which are in the retrieved chunks. |
| 11 | `tr_20260905T1506_0062` | The answer said the BP-2 exception does not apply where the dwelling is the primary place of business, and used `【 】` around its source tag. |
| 12 | `tr_20260905T1633_0064` | The answer walked from the single weekly visit in BP-2 to the void clause in BP-4 and concluded no, citing both. |
| 13 | `tr_20260906T0853_0066` | The answer said yes and quoted the E-39 domestic workers row; two of the five chunks in context came from HO-0305 and HO-0307 and went unused. |
| 14 | `tr_20260906T1708_0074` | The answer said yes and cited `HO-0306_sa_chunk_005` as CLAUSE-WD-1 of HO-0306, a clause number that lives in HO-0304, and it did not mention the 72-hour report or the licensed contractor estimate that MF-2 attaches to the $10,000. |
| 15 | `tr_20260908T0959_0090` | The assistant refused a claim status question; the retrieved chunks scored lower than anywhere else I read and came from three different forms. |
| 16 | `tr_20260908T1518_0096` | The assistant refused the ISO form equivalence question, and the five retrieved chunks were all preamble blocks. |
| 17 | `tr_20260909T1208_0106` | To the three words "what about earthquake" the answer said earthquake losses are not covered by this endorsement, naming HO-0308 only inside the citations, while HO-0307's own E-31 row sat at rank 3 in the same context. |
| 18 | `tr_20260909T1719_0113` | To the two words "burst pipe" the answer said covered and quoted E-17, WD-1 and WD-2, with all three source tags in `【 】`. |
| 19 | `tr_20260911T1220_0130` | Asked a leading question that asserted the sublimit sits on top of Coverage A, the answer said no and cited MF-4. |
| 20 | `tr_20260911T1659_0134` | To "e-36?" the answer returned home day care and foster care liability from the HO-0309 table; the other four chunks in context carried no BM25 rank at all. |

Clustering these 20 sentences produced the 6 named modes in `taxonomy.md`.

---

## 3. What each mode looks like

**Mode 1 — citation printed in brackets the citation checker cannot parse (4, 20%).**
The source tag comes back as `【SOURCE: … 】` instead of `[SOURCE: … ]`. The content is
right every time; nothing that reads citations programmatically can see it. Traces
`0004`, `0043`, `0062`, `0113`.

**Mode 2 — denial text that cannot be pasted into a letter as written (2, 10%).**
The coverage call is correct and the sentence is still not usable. `0009` opens *"The loss
is covered by exclusion E-14"* on a claim that row denies; `0054` says mining subsidence is
excluded and never prints code E-32, which is the thing the denial letter needs.

**Mode 3 — widens a narrowly scoped clause into a general rule (1, 5%).**
CLAUSE EM-4 makes the Company's engineering report controlling on *whether earth movement
contributed*. In `0057` the answer made it controlling on the cause of loss generally, in a
settlement-versus-construction-defect dispute where that is exactly the contested question.

**Mode 4 — answers a corpus-wide question from one endorsement only (1, 5%).**
"what about earthquake" in `0106` was answered as HO-0308's rule and stated as the whole
answer. HO-0307's own E-31 row, which reaches scheduled items, sat at rank 3 in the same
context and went unmentioned.

**Mode 5 — cites a clause number that does not exist in the form it names (1, 5%).**
`0074` emits `[SOURCE: HO-0306_sa_chunk_005 | HO-0306 | CLAUSE-WD-1]`. WD-1 is a HO-0304
clause. The chunk is the tail of HO-0306's MF-2, split at an inline cross-reference to that
clause, and the chunker took the referenced clause as the chunk's own label — the only one
of 72 chunks with a cross-form clause label. An adjuster who checks the citation finds
nothing, and the chunk itself starts mid-sentence.

**Mode 6 — refuses although the answering exclusion row is in the corpus (1, 5%).**
`0049` asked about government seizure of a scheduled item. Five HO-0307 clause chunks came
back with no exclusion table among them, so the model refused correctly given its context.
HO-0307's table carries an E-32 government action row.

---

## 4. Replay evidence

Trace picked at random by trace_id, **seed `5091`**, `n=1`, over the same 140-trace
population (`traces/replay_pick.json`):

```
tr_20260907T1339_0083
```

Replayed with `python week5_analysis.py replay tr_20260907T1339_0083`. Full transcript in
`traces/replay_evidence.md` — original output next to the replayed output.

### What the trace could and could not give back

The trace log this week was written under **schema v1.0**, which records the redacted
question, every retrieved chunk_id with its fused score and dense/BM25 provenance, the model
name, temperature and max_tokens, and the raw output. Replaying it exposed three holes:

| Field | v1.0 |
|---|---|
| Prompt version | **Missing.** The app had never versioned its prompt, so the replay had to take the system prompt and user template from current source and could not prove that is what ran. |
| Corpus fingerprint | **Missing.** Chunk text is recovered by resolving chunk_ids against `chroma_db`, with nothing in the trace to prove the index still holds the same text. |
| Response metadata | **Missing.** No finish_reason, no token usage, no provider response id. |

All three were added in **schema v1.1**: `prompt.version` plus a SHA-256 of the rendered
system+user request, a corpus fingerprint over every (chunk_id, text) pair, a per-chunk
`text_sha256`, and the provider's response id, finish reason and usage. `src/prompts.py` now
holds the prompt registry, and it refuses to load if the text of a version that traces
already cite has been edited in place.

**What still cannot be reconstructed, and will not be:** the provider-side sampling seed.
Groq does not echo it back, so an identical replayed output is evidence of determinism at
`temperature=0.0`, not proof of it.

---

## 5. Redaction — before write, not after

Claimant names, claim numbers, policy numbers, phone numbers, email addresses and street
addresses are removed by `src/redaction.py` inside `tracing.answer_and_trace`, **before the
trace record is built** and before the question is sent anywhere. `tracing.write_trace` then
re-scans the serialised record with the same detectors and raises `RedactionError` instead of
appending the line if anything still matches. A trace file that exists on disk is therefore a
trace file that passed the guard; there is no cleanup pass over an existing log.

Confirmation on the sample: 4 of the 20 traces carry a redaction count, 16 needed none, and
every identifier the roster fed in came back as `[CLAIMANT_NAME]`, `[CLAIM_NUMBER]` or
`[POLICY_NUMBER]`. Form numbers, edition dates and exclusion codes are untouched, which is
what makes the redacted log still readable as claims text.

Stated limit rather than hidden: the person-name detector combines titles, claims keywords
and a first-name gazetteer. A bare surname that is in none of those would not be caught.

---

## 6. The dated prediction

Committed **before any fix**, in `prediction.md`.

> **2026-09-07** — Mode 1, "citation printed in brackets the citation checker cannot parse",
> stands at **4/20 = 20%**. Adding a citation normaliser that rewrites `【SOURCE: …】` to
> `[SOURCE: …]` and folds non-breaking hyphens to ASCII before a trace is written will drop
> that mode to **at most 1/20 = 5%** on a fresh seeded sample of 20 traces drawn from a new
> week of traffic, measured on **2026-09-14**, with **hit-rate@3 unchanged at 12/12** on
> `golden_set.jsonl`.

Commit hash: `8b109ff18f6a579a73967ff9863c6d61c5013519`, dated 2026-09-07.

Wrong if the mode stays above 5%, or if hit-rate@3 moves at all.

---

## 7. Why a public benchmark would have missed the top three modes

A public retrieval or QA benchmark scores whether the answer text matches a reference, so
mode 1 is invisible to it by construction: every one of those four answers is factually
right and would score a clean hit, and the bracket character that breaks our citation
checker is not part of any benchmark's answer key. Mode 2 fails on a property no benchmark
measures either, because "correct" and "safe to paste into a denial letter" are different
tests, and only the second one has a bad-faith exposure attached to it. Mode 3 needs a grader
who knows that CLAUSE EM-4 makes an engineering report controlling on earth movement and
nothing else, which is a fact about six synthetic endorsements that exist only in this repo
and could not appear in any public corpus.

---

## 8. Bonus — the curated demo set

The monthly-review deck is `simulate_traffic.py`'s `DEMO_BANK`: the ten questions the team
always shows, all well-formed, all single-form, all answered correctly the first time they
were ever run. They were fired at the same pipeline and logged to `traces/demo.jsonl`.

**Partial run.** Groq's free tier caps this model at 200,000 tokens per day, and generating
the 140-trace population spent it. Four of the ten demo traces exist; the run is still
waiting on the daily window for the other six. The numbers below are over the four, and are
labelled as such rather than presented as ten.

| # | trace_id | What I saw |
|---|---|---|
| 1 | `tr_20260828T1437_0001` | To the flagship mold question the answer gave $10,000, wrapped the source tag in `【 】`, cited `HO-0306_sa_chunk_005` as CLAUSE-WD-1 of HO-0306, and replaced MF-2's two conditions with the phrase "when the required conditions are met". |
| 2 | `tr_20260828T1604_0002` | The answer restated EM-2's concurrent causation rule in full, with a square-bracket citation to the EM-2 chunk. |
| 3 | `tr_20260828T1718_0003` | The answer said 36 months and cited SECTION-III, with square brackets. |
| 4 | `tr_20260829T0923_0006` | The answer said $6,000 and cited the worked example in SECTION-III, with square brackets. |

### The two numbers

| | Random sample | Demo set |
|---|---|---|
| Top mode — citation the checker cannot parse | **4 / 20 = 20%** | **1 / 4 = 25%** |

### What the team has been telling itself

For a month the demo deck has been evidence that the assistant works, and on the four
questions read here it does: every coverage call is right, every number is right, and the
one thing that is wrong is the thing a demo never tests. The flagship mold question — the
first slide, the one everybody has seen — emits a citation in brackets no checker can read
and points it at `CLAUSE-WD-1 of HO-0306`, a clause that exists only in HO-0304. Nobody
noticed, because in a demo the citation is a visual reassurance rather than a link anyone
follows. The demo set was picked for questions with clean single-form answers, so it
selects for the cases that work and is blind by construction to the modes that matter:
there is no edition the corpus lacks, no exclusion code that collides across two forms, no
procedural question, no two-word query. What the team has been telling itself is that a
deck of ten questions chosen because they worked is evidence that the app works. It is
evidence that those ten questions work, and even that is not quite true — the top mode
shows up in the demo set at the same rate as in real traffic, on the slide shown first.
