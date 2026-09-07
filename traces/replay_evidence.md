# Replay evidence — one trace, rebuilt from the trace alone

## How the trace was picked

Seeded, over the same 140-trace population, drawn separately from the sample of 20:

```bash
python week5_analysis.py sample --seed 5091 --n 1 --out traces/replay_pick.json
```

```
population : 140 traces in traces/traffic.jsonl
seed       : 5091
rule       : random.Random(seed).sample(sorted(trace_ids), 1)
selected   : tr_20260907T1339_0083
```

## The trace

```
trace_id : tr_20260907T1339_0083
ts       : 2026-09-07T13:39:00      channel: portal_widget      schema: v1.0
question : Does HO-0308 ed. 04-24 include the concurrent causation rule?
           (redaction: none needed)

retrieved (fused_rrf, k=5):
  1. HO-0308_sa_chunk_004  score=0.03279  dense=1 bm25=1  HO-0308 ed.05-24  CLAUSE-EM-2
  2. HO-0308_sa_chunk_008  score=0.03200  dense=2 bm25=3  HO-0308 ed.05-24  EXCLUSION-TABLE
  3. HO-0308_sa_chunk_009  score=0.03200  dense=3 bm25=2  HO-0308 ed.05-24  CLAUSE-EM-3
  4. HO-0305_sa_chunk_005  score=0.03125  dense=4 bm25=4  HO-0305 ed.03-24  CLAUSE-NS-3
  5. HO-0308_sa_chunk_007  score=0.02899  dense=9 bm25=9  HO-0308 ed.05-24  SECTION-II

model : openai/gpt-oss-120b   temperature=0.0   max_tokens=800
```

The adjuster asked about **HO-0308 ed. 04-24**. Only ed. 05-24 is indexed, and the
assistant refused rather than answering from the edition it did have.

## Reproducing it

```bash
python week5_analysis.py replay tr_20260907T1339_0083
```

## Reconstruction manifest

```
RECONSTRUCTION MANIFEST
  question (redacted)            FROM TRACE
  retrieved chunk_ids + scores   FROM TRACE
  chunk text                     FROM INDEX (resolved by chunk_id)
  system prompt                  FROM CODE (trace has no prompt_version)
  user template                  FROM CODE (trace has no prompt_version)
  model name                     FROM TRACE
  temperature / max_tokens       FROM TRACE
  original raw output            FROM TRACE
  prompt hash check              UNRECOVERABLE (v1.0 stored no rendered prompt hash)
  corpus fingerprint             UNRECOVERABLE (v1.0 stored no fingerprint)
  provider-side sampling seed    UNRECOVERABLE (Groq does not echo it back)

  rebuilt prompt: 1164 char system + 3124 char user  (sha256 82f1ad652c682816)
```

## Original vs replayed

```
==============================================================================
ORIGINAL OUTPUT (from the trace, 2026-09-07T13:39:00)
==============================================================================
REFUSAL: The requested information (e.g. HO-0308 ed. 04-24 concurrent causation
rule) is not present in the indexed endorsement corpus. This question cannot be
answered from the available policy documents.

==============================================================================
REPLAYED OUTPUT (re-run just now)
==============================================================================
REFUSAL: The requested information (e.g. HO-0308 ed. 04-24 concurrent causation
rule) is not present in the indexed endorsement corpus. This question cannot be
answered from the available policy documents.

==============================================================================
identical: True    similarity: 1.0000    refusal original=True replayed=True
==============================================================================
```

Byte-identical, including the parenthetical topic the model chose for its refusal.

## The fields that were missing, and what was done about them

Three lines in the manifest say `FROM CODE` or `UNRECOVERABLE` because of the
schema, not because of physics. Those are holes.

| Field | v1.0 | v1.1 |
|---|---|---|
| Prompt version | Absent — the replay took the system prompt and user template from current source and could not prove that is what ran | `prompt.version` plus `prompt.rendered_sha256`, a SHA-256 over the rendered system+user request |
| Corpus fingerprint | Absent — chunk text recovered from the live index with nothing to check it against | `retrieval.corpus_fingerprint`, a hash over all 72 (chunk_id, text) pairs, plus `text_sha256` on every hit |
| Response metadata | Absent | `finish_reason`, `response_id`, and prompt/completion/total token usage |

`src/prompts.py` holds the registry and refuses to import if the text of a
version that existing traces cite has been edited in place; `src/answerer.py`
carries a tripwire copy of v1 so drift fails loudly at import rather than
silently at replay time.

## What still cannot be reconstructed

**The provider-side sampling seed.** Groq does not return it, so it cannot be
pinned or replayed. The identical output above is evidence that this request is
deterministic at `temperature=0.0`; it is not proof that it always will be. No
schema version can close this one, and it is recorded as permanent rather than
pending.
