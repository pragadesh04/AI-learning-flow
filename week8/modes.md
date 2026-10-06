# Week 8 failure-mode zoo and counts

A case can carry more than one mode. The counts are independent, so a mitigation that fixes one mode while breaking another shows up as a negative number in a row nobody was watching.

| mode | what it is | before | after | after + defences |
|---|---|---|---|---|
| M1 | skipped the exclusion lookup and still answered | 0 | 0 | 0 |
| M2 | computed a payout before reading the wording | 0 | 0 | 0 |
| M3 | called a tool with arguments that do not resolve | 0 | 0 | 0 |
| M4 | thrash: a repeated call, or a budget stop with no answer | 1 | 2 | 4 |
| M5 | right path, wasted laps | 1 | 2 | 4 |
| M6 | no fault observed | 9 | 8 | 6 |
