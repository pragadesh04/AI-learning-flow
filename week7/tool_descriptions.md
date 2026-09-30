# Week 7 — the three tool descriptions

`get_claim` and `search_policy` are the two the task hands you. The diff below is for the third one, which is the one the rubric scores: one job, an enum on the claim-status parameter, and no wording shared with the other two.

## The third tool, and the diff

```diff
  # v1 — the first draft, the way the other two are written: two jobs, hedged
  + "Look up the claim and its exclusions, then work out how much is payable.
  +  Useful when you need the claim details, the applicable exclusion codes and
  +  the payment calculation together."
- "Apply one policy excess to one already-adjudicated covered amount and return
-  the payable figure with the arithmetic. This tool returns money only. It does
-  not read policy wording and it does not decide whether a loss is covered."
```

The v1 draft says "claim", "exclusions" and "calculation" in one sentence, so a model reading it has three reasons to reach for it at step one. The shipped version says what it does, and then says the two things it does not do, which is where the separation actually lives.

## All three, as sent

### `get_claim`

```
Read the adjuster system and return the claim file filed under one claim number: date of loss, policy forms in force, amount claimed, the excess on file, and the adjuster's notes. This tool returns what was claimed. It does not return policy wording and it does not calculate anything.
```

### `search_policy`

```
Search the indexed endorsement wording and return the clause text that governs a named peril, with its clause id and exclusion codes. This tool returns what the policy says. It does not know about any individual claim and it does not calculate anything.
```

### `compute_payout`

```
Apply one policy excess to one already-adjudicated covered amount and return the payable figure with the arithmetic. This tool returns money only. It does not read policy wording and it does not decide whether a loss is covered.
```

## Overlap check

| description | job words | shared with another tool |
|---|---|---|
| `get_claim` | claim, notes, adjuster system | wording (with search_policy), policy (with search_policy), excess (with compute_payout), amount (with compute_payout) |
| `search_policy` | wording, endorsement, clause, peril, policy | claim (with get_claim) |
| `compute_payout` | excess, arithmetic, money, payable, amount | wording (with search_policy), policy (with search_policy) |

Read the middle column before reading the prose: the three descriptions DO share nouns,
and deliberately so. Each one ends by naming what it does not do, and you cannot say
"it does not read policy wording" without using the words policy and wording. The
overlap that matters is not lexical, it is directional: a word that appears in a
description followed by a *negation* is a word that pushes the model away. The
only genuinely shared noun is *amount*, which is the same word for two different
numbers (claimed vs payable), and the two sentences separate those by what
the tool does with the number rather than by the number itself. `compute_payout`
is the only one of the three that subtracts anything.

## The enum

`compute_payout.claim_status` is a closed set of six workflow states:

- `open`
- `under_review`
- `partially_approved`
- `approved`
- `denied`
- `withdrawn`

They are workflow states, not triage verdicts. `PAY`/`DENY`/`REFER` are the output contract's business and appear nowhere in the tool's parameters, because a tool that accepts `denied` as an argument will be called with `denied` and the caller will stop thinking. A claim_status the enum does not contain is a week-8 argument-validity failure, and it is checked offline in `agent_tools.argument_problems`.

