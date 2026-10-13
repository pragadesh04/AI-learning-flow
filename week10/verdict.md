# Verdict: KILL the squad, keep the single agent

1. Sunk-cost bias, named out loud: I built the orchestrator last week, and "but we already built it" is not a reason to ship it. The table decides.
2. Quality: both arms pass 1/10 on the full Week-6 ruler, because A1 (the `CLM-` claim-number format) sinks both equally. On the judged criterion (COVERAGE_SUPPORTED) the single agent wins 7/10 to 3/10.
3. Tokens: 96,993 vs 55,882, a **1.7x** re-send multiplier. 71% of squad tokens are the orchestrator -> exclusions_worker hand-off.
4. Cost per claim: $0.002593 vs $0.001275, **2.0x** (the extra planner and notes-worker calls are mostly priced completion tokens).
5. Latency: p50 10.48s vs 3.89s, p99 18.06s vs 8.87s. Even with the two workers run concurrently the squad is p50 8.86s / p99 16.15s, still over 2x.
6. Where the quality went: the hand-offs. On s11 the planner never asked about the $600 air sampling, so MF-3 was never searched and synthesis wrote "None identified". On s20 synthesis rounded "may be reclassified under E-11" up to "Coverage denied".
7. Failure mode: with the exclusions worker down, the squad wrote "EXCLUSIONS APPLIED: None", which is worse than the single agent, which has no worker to lose.
8. No claim class in these 10 needs decomposition: every case is one claim file with one or two perils that a single loop searches in 2–7 laps.
9. Kill condition I'd revisit: claim files with many independent perils across several forms, where workers truly run in parallel and the planner is evaluated on its own.
