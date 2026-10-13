# Bonus — AgentCard and the failed case on the A2A task lifecycle

The card the orchestrator would advertise is `week10/agent_card.json`. It has one skill, `summarise-claim-file`, takes `application/json` in and returns `text/plain` out, uses a bearer token scoped to `claims:summary:read` only (no payment or settlement scope), and doesn't stream.

## s05 under the 500, mapped onto the lifecycle

| A2A state | what the squad did as built | what it should have done |
|---|---|---|
| `submitted` | case s05 accepted | same |
| `working` | plan, then exclusions worker -> 500, retry -> 500 | same, up to the second 500 |
| `input-required` | **skipped** | **pause here**: "Exclusions check unavailable (HTTP 500 ×2). Re-run the check, or confirm you'll adjudicate exclusions by hand?" The adjuster's answer resumes the task into `working` |
| `completed` | **reached**, with "EXCLUSIONS APPLIED: None" | only after a real exclusions finding exists |
| `failed` | not used | correct if no adjuster is on the other end (batch triage). Returning *no* summary is safer than a clean-looking one |

The task should have stopped at `input-required`, waiting for the adjuster's confirmation. Ending it as `completed` with a filled-in EXCLUSIONS APPLIED line was the bug.

## What A2A buys over a plain REST call to the worker

1. With A2A, a long or failed delegation is a task with explicit states (`working`, `input-required`, `failed`) that the caller has to handle. A REST call just returns a 500 that the caller can swallow into a string, which is exactly what this orchestrator did.
2. The AgentCard declares the worker's skills, input/output modes and auth scope up front. The orchestrator discovers what it's allowed to ask for, instead of hard-coding an endpoint and assuming its contract.
