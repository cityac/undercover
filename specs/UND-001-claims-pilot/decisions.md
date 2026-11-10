# Decisions Log — Claims Pilot (UND-001)

Audit trail of autonomous spec clarification. Source: `consensus-report.md` (5 agents).

## Decisions

### Decision: Atomic decision and payment; what a failure undoes
**Issue:** "No partial decision on failure" conflicted with payments that cannot be rolled back and with over-limit payment refusals.
**Resolution:** An in-limit approval and its payment are recorded together or not at all. Any failure before the claim reaches `decided` or `waiting for sign-off` discards the decision and returns the claim to `waiting`. Once a payment exists the claim is `decided`. A refused payment is a step, not a failure. Steps are always kept, tagged with the run id.
**Rationale:** Prevents double payment and orphan approvals.
**Consensus:** consensus (5/5)

### Decision: One guarded payment path; sign-off pays through it
**Issue:** Unclear whether sign-off pays itself or unlocks a separate payment call.
**Resolution:** All payments go through one guarded operation (approved, amount equals payout, not paid before, signed off if over the limit). Sign-off records handler and time and then pays through that guard in one transaction. A second sign-off or payment is refused.
**Rationale:** A single enforcement point for the $1,000 rule.
**Consensus:** consensus (5/5)

### Decision: Sign-off identity check
**Issue:** `can_approve_over_limit` not enforced; any name could be sent.
**Resolution:** Sign-off is refused for an unknown handler or a handler whose flag is false. This is bookkeeping, not authentication (no sign-in in the pilot).
**Rationale:** Uses the business data as given; honest about the limit.
**Consensus:** consensus (5/5)

### Decision: Make refer visible
**Issue:** A referred claim is `decided`, which hides that a person must act.
**Resolution:** Keep the four states from `docs/SPEC.md`. Show the outcome (approve, decline, refer) as its own label next to the state, in the queue and on the claim page.
**Rationale:** No new states beyond the customer's list.
**Consensus:** consensus (5/5)

### Decision: Wording-only decision rules
**Issue:** `docs/SPEC.md` ties refer to the claims manual, which is out of scope.
**Resolution:** Refer when a required document is missing (section 11), the facts or documents are unclear or contradictory, or the wording does not settle the case; when unsure, refer. Decline when the wording clearly excludes the claim. An incident outside the covered trip dates is a decline citing section 9, except a return delay that section 3 covers. A claim filed more than 90 days after the incident is a refer citing section 11.
**Rationale:** Conservative; a person judges where the wording gives no consequence.
**Consensus:** consensus (5/5) on wording-only; late filing was a 2/2 divergence → conservative (refer).

### Decision: Claim history is context only
**Issue:** History is an input but only manual rules use it.
**Resolution:** The agent reads history as context; manual-only rules (repeat claims, meals without receipts, wild animals) are not applied; doubt the wording cannot settle → refer.
**Rationale:** Keeps the manual out of scope as the customer asked.
**Consensus:** consensus (5/5)

### Decision: Release a stuck claim
**Issue:** A crashed run leaves a claim `in progress` forever.
**Resolution:** A release command, not available to the agent, moves an `in progress` claim with no decision back to `waiting` and adds an error step. No automatic timeout.
**Rationale:** Recovery without wiping other work.
**Consensus:** consensus (4/5)

### Decision: Explanation length check
**Issue:** Hard sentence counting is brittle (`$1,000.50`, "Sec. 5").
**Resolution:** The 2–3 sentence rule is in the instructions and checked in tests. The backend refuses only an empty explanation or one over 600 characters.
**Rationale:** Avoids false refusals; still bounded.
**Consensus:** consensus (4/5)

### Decision: Reset is an explicit local command
**Issue:** When data loads and who can wipe it.
**Resolution:** Data is seeded only into an empty store. Resetting needs an explicit command. Restarting keeps all work. Reset is not on the dashboard and not reachable by the agent.
**Rationale:** Protects the record of decisions and payments.
**Consensus:** consensus (4/5)

### Decision: Agent tool allow-list
**Issue:** Without sign-in, the agent could call sign-off or reset.
**Resolution:** The agent's tools are limited to reading (claim, policy, history, wording, instructions), recording a decision and paying. No sign-off, release or reset tool. A test checks the tool list.
**Rationale:** Enforces "even if the agent tries" by construction.
**Consensus:** consensus (4/5)

### Decision: Instructions source
**Issue:** No source for the instructions text.
**Resolution:** One committed text file, served read-only by the backend; the agent and the dashboard read it from the same operation; it never refers to `data/evals/`.
**Rationale:** Single source of truth; read-only as required.
**Consensus:** consensus (3/5)

### Decision: Working the queue
**Issue:** Batch order and failure handling unspecified.
**Resolution:** Waiting claims are worked one at a time in queue order; a failed claim returns to waiting, the run continues, and a summary lists failures.
**Consensus:** consensus (3/5)

### Decision: No reject at sign-off
**Issue:** A wrong over-limit approval cannot be sent back.
**Resolution:** Out of scope for the pilot; the claim page states that sign-off only releases the payment. Recorded as an open question for the head of claims.
**Consensus:** consensus (3/5)

### Decision: Payout cap
**Issue:** The backend accepted payouts above the plan's benefit maximum.
**Resolution:** An approval is refused if the payout exceeds the amount claimed or the plan's maximum for the claimed benefit. The exact calculation stays with the agent.
**Rationale:** Conservative for money; accuracy is measured in a later build.
**Consensus:** divergence (2/5) → conservative

### Decision: Queue order
**Issue:** "In the order submitted" is false for the data (`submitted_on` is not monotonic).
**Resolution:** Queue order is the record order (claim id); the submitted date is shown.
**Consensus:** divergence (2/5), verified against data

### Decision: Success criterion for a full run
**Issue:** SC-002 could not be verified without a real model.
**Resolution:** With the scripted stand-in, all 25 claims end decided or waiting for sign-off. A live run leaves no claim in progress and reports failures.
**Consensus:** divergence (2/5) → adopted

### Decision: Exact money
**Issue:** Money representation unspecified.
**Resolution:** Amounts are exact to the cent; more than two decimals is refused. Representation chosen in the plan.
**Consensus:** divergence (2/5)

### Decision: $0 approval
**Issue:** Edge case read as if the system rewrites the outcome.
**Resolution:** An approval of $0.00 is refused; the agent must record a decline. The system never rewrites the agent's outcome.
**Consensus:** outlier (1/5), genuine gap

### Decision: Personal data
**Issue:** Customer contact details could reach the model and the step log.
**Resolution:** The agent gets the customer's id, name and previous claims only; no email, phone, address or date of birth. The dashboard shows name and previous claims.
**Consensus:** outlier (1/5), genuine gap

### Decision: Calculation on the decision
**Issue:** A handler cannot check a payout at sign-off.
**Resolution:** Each decision carries a short calculation text (for approvals: how the payout was reached; otherwise a one-line note).
**Consensus:** outlier (1/5), genuine gap

### Decision: Currency
**Issue:** One claim's documents are in euros.
**Resolution:** Use the USD item amounts on the claim; never convert; refer if the dollar amount is not established.
**Consensus:** outlier (1/5), genuine gap

### Decision: Payment refusal steps
**Issue:** "Refusal by anyone else appears as a step" conflicts with steps belonging to runs.
**Resolution:** A refusal is a step when it comes from an agent run; other callers just get the refusal.
**Consensus:** outlier (1/5), simplification
