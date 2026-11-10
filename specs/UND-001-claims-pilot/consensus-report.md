# Stochastic Multi-Agent Consensus Report — UND-001 Claims Pilot spec

**Problem**: Find ambiguous, missing and contradictory requirements in `spec.md`; propose conservative resolutions.
**Agents**: 5 (sonnet) — framings: neutral, risk-averse, contrarian, first-principles, handler-empathy
**Date**: 2026-11-10
**Note**: no agent opened `data/evals/`.

## Consensus (3+/5)

| # | Issue | Agents | Resolution adopted |
|---|---|---|---|
| C1 | Failure rollback vs recorded payment; payment refusal vs failure | 5/5 | Decision + in-limit payment are atomic; a failure before an end state discards the decision and returns the claim to waiting; once paid it is decided; an over-limit refusal is a step, not a failure; steps kept with run id |
| C2 | Sign-off: does it pay itself or call the pay operation? | 5/5 | One guarded pay path; sign-off records handler+time and pays through it in one transaction; second sign-off/payment refused |
| C3 | `can_approve_over_limit` / known handler not enforced | 5/5 | Sign-off refused for unknown handler or flag false; trust-based, not authentication |
| C4 | Refer hidden inside `decided` | 5/5 | Keep 4 states; outcome badge (approve/decline/refer) in queue and claim page |
| C5 | Refer/decline rules with manual out of scope | 5/5 | Wording-only rules; refer on missing document, unclear facts or unsettled wording; when unsure, refer |
| C6 | How claim history is used | 5/5 | Context only; manual-only rules not applied; refer when history raises doubt the wording cannot settle |
| C7 | Crashed run leaves claim `in progress` forever | 4/5 | Release command (not an agent tool) moves an undecided in-progress claim to waiting with an error step |
| C8 | 2–3 sentence rule as hard backend validation | 4/5 | Rule lives in instructions and tests; backend checks non-empty and ≤ 600 characters |
| C9 | Reload could wipe work; when does it run | 4/5 | Explicit reset command only; seed only an empty store; restart keeps work; not on dashboard; not reachable by agent |
| C10 | Agent could call sign-off / reset (no sign-in) | 4/5 | Agent tool allow-list: reads, start, record decision, pay; tested to exclude sign-off/reset/release |
| C11 | Source of the instructions text | 3/5 | One committed file, served read-only by the backend; agent and dashboard read the same operation |
| C12 | Batch run order and failures | 3/5 | Sequential; continue past failures; summary lists failed claims |
| C13 | No reject at sign-off | 3/5 | Out of scope; stated as a known limit |

## Divergence (2/5 vs 2/5)

| # | Issue | Split | Resolution |
|---|---|---|---|
| D1 | Filed > 90 days after incident | decline (neutral, contrarian) vs refer (risk-averse, first-principles) | Refer, citing section 11 — the wording states the window but no consequence; a person judges (conservative) |
| D2 | Backend payout cap beyond amount claimed | add plan-maximum cap (risk-averse, empathy) vs none | Add cap: payout ≤ amount claimed and ≤ the plan's maximum for the benefit (conservative for money) |
| D3 | Queue order | claim-id/file order (neutral, first-principles) vs unspecified | File order (claim id); submitted date shown. Verified: `submitted_on` is not monotonic |
| D4 | SC-002 unverifiable with a real model | split CI/live (risk-averse, first-principles) | Split: scripted run must end 25/25; live run reports failures |
| D5 | Money representation | cents/decimal (risk-averse, first-principles) | Exact to the cent, no floating point (plan-level) |

## Outliers adopted (genuine gaps)

- O1 (contrarian): approve with $0.00 is refused, never rewritten to decline.
- O2 (risk-averse): contact details (email, phone, address, date of birth) not given to the agent; dashboard shows name only.
- O3 (handler-empathy): decision carries a short calculation so a handler can check the payout at sign-off.
- O4 (first-principles): use the claim's USD item amounts; no currency conversion; refer if the dollar amount is not established.
- O5 (first-principles): incident outside trip dates → decline citing section 9, except a return delay extended by section 3.
- O6 (neutral): payment refusals are steps only when they come from an agent run.

## Outliers not adopted

- Refuse reset while a claim is in progress (1/5) — reset is a deliberate local command; low value.
- Queue filters by state/outcome (2/5) — badge meets the need for 25 claims; filters are UI extras not asked for.
- Demote numeric UI timings (1/5) — kept as targets; polling satisfies them cheaply.
