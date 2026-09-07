# Failure taxonomy — insurance claims assistant

20 traces drawn at random from 140 in `traces/traffic.jsonl`, seed `20260907`, read by
hand on 2026-09-07 with zero code changes. Sentences in `notes.md`, coding in
`traces/coding.csv`, counts from `python week5_analysis.py tally`.

| # | Failure mode | Count | Freq % | Severity | Example trace_id |
|---|---|---|---|---|---|
| 1 | Citation printed in brackets the citation checker cannot parse | 4 | 20% | Annoys the adjuster | `tr_20260831T1225_0004` |
| 2 | Denial text that cannot be pasted into a letter as written | 2 | 10% | Misleads the adjuster | `tr_20260831T1556_0009` |
| 3 | Widens a narrowly scoped clause into a general rule | 1 | 5% | Wrongly denies or pays | `tr_20260905T0939_0057` |
| 4 | Answers a corpus-wide question from one endorsement only | 1 | 5% | Wrongly denies or pays | `tr_20260909T1208_0106` |
| 5 | Cites a clause number that does not exist in the form it names | 1 | 5% | Misleads the adjuster | `tr_20260906T1708_0074` |
| 6 | Refuses although the answering exclusion row is in the corpus | 1 | 5% | Misleads the adjuster | `tr_20260904T1244_0049` |
| — | No fault observed | 10 | 50% | — | `tr_20260901T1148_0015` |

**Half the sampled traces carry a defect an adjuster would notice.** Nothing in the sample
invented a coverage rule that is not in the documents, and 10% of traces show a defect that
could send a claim the wrong way.

**Next week:** mode 1, at four times the next-largest mode. Dated, falsifiable prediction in
`prediction.md`, commit `8b109ff`, made before any fix.

*What each mode looks like, with the evidence: `notes.md` §2 and §3.*
