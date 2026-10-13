# Week 10 race — single agent vs claims squad

Same 10 Week-6 summary cases (seeded stratified sample, seed 20261012): s01, s05, s06, s09, s11, s14, s15, s19, s20, s23.
Same ruler: 5 Week-6 assertions + judge_v1 (COVERAGE_SUPPORTED); pass = all applicable assertions pass AND judge PASS.
Same model (openai/gpt-oss-120b, temperature 0), same search_policy tool, same budget ledger.

| metric | single agent | squad (orchestrator + 2 workers) |
|---|---|---|
| pass rate | 1/10 = 10% | 1/10 = 10% |
| p50 latency (s) | 3.89 | 10.48 |
| p99 latency (s) | 8.87 | 18.06 |
| total tokens (10 claims) | 55,882 | 96,993 |
| cost per claim | $0.001275 | $0.002593 |

**Context re-send multiplier: 96,993 / 55,882 = 1.7x.** Largest token share: `orchestrator->exclusions_worker`, 69,207 tokens = 71% of all squad tokens.

Squad tokens by hand-off (all 10 cases):

| hand-off | calls | prompt | completion | total | share |
|---|---|---|---|---|---|
| orchestrator->exclusions_worker | 46 | 59,579 | 9,628 | 69,207 | 71% |
| workers->orchestrator.synthesise | 10 | 6,171 | 6,105 | 12,276 | 13% |
| orchestrator.plan | 10 | 3,550 | 4,754 | 8,304 | 9% |
| orchestrator->notes_worker | 10 | 2,410 | 4,796 | 7,206 | 7% |

Per case:

| case | mode | single: assertions / judge / PASS | tokens | latency s | squad: assertions / judge / PASS | tokens | latency s |
|---|---|---|---|---|---|---|---|
| s01 | denial text that cannot be pasted into | XX A1 / PASS / FAIL | 2,462 | 3.16 | XX A1 / PASS / FAIL | 4,469 | 6.74 |
| s05 | denial text that cannot be pasted into | XX A1,A5 / PASS / FAIL | 7,626 | 6.07 | XX A1 / PASS / FAIL | 13,588 | 11.46 |
| s06 | widens a narrowly scoped clause into a | XX A1,A5 / FAIL / FAIL | 3,877 | 2.97 | XX A1,A5 / FAIL / FAIL | 4,126 | 6.60 |
| s09 | widens a narrowly scoped clause into a | XX A1,A5 / FAIL / FAIL | 7,961 | 5.89 | XX A1 / FAIL / FAIL | 8,082 | 9.61 |
| s11 | answers a corpus-wide question from on | XX A1 / PASS / FAIL | 4,052 | 3.76 | XX A1 / FAIL / FAIL | 6,483 | 9.28 |
| s14 | answers a corpus-wide question from on | XX A1,A5 / FAIL / FAIL | 13,759 | 8.87 | XX A1,A3,A4 / FAIL / FAIL | 17,883 | 18.06 |
| s15 | cites a clause number that does not ex | XX A5 / PASS / FAIL | 5,839 | 5.66 | XX A2,A3,A5 / FAIL / FAIL | 8,268 | 11.35 |
| s19 | cites a clause number that does not ex | XX A5 / PASS / FAIL | 5,653 | 4.02 | XX A5 / FAIL / FAIL | 12,673 | 14.02 |
| s20 | citation printed in brackets the citat | ok / PASS / PASS | 2,462 | 2.92 | XX A5 / FAIL / FAIL | 17,638 | 14.38 |
| s23 | refuses although the answering exclusi | XX A4 / PASS / FAIL | 2,191 | 2.41 | ok / PASS / PASS | 3,783 | 6.48 |

Notes on the numbers:

- Latency is summed model time + tool time as executed (the Week-7 work clock); the provider's rate-limit queue is excluded. The squad ran its two workers one after the other; if they ran concurrently its critical path would be p50 8.86s / p99 16.15s.
- p99 over 10 runs is nearest-rank, i.e. the slowest run. It is reported because the slowest claim is the one that gets complained about.
- Cost uses the notional tariff from Week 7 ($0.15/Mtok prompt, $0.6/Mtok completion) on metered tokens; Groq's free tier bills $0.
- Assertions passed: single 1/10, squad 1/10. Judge PASS: single 7/10, squad 3/10.
- Judge calls are the eval's cost and are in neither arm's tokens.
