# Feature Specification: Claims Pilot

**Feature Branch**: `feature/UND-001-claims-pilot`
**Created**: 2026-11-10
**Status**: Draft
**Input**: `docs/SPEC.md` (from UnderCover's head of claims operations). User description: "Claims pilot per docs/SPEC.md: backend seeded from data/, the UnderCover Agent decides each claim through the backend only, dashboard for handlers with the queue, claim detail, live agent steps and read-only instructions; payouts over $1,000 blocked until a handler signs off; data/evals/ never seen by the agent; not in scope: claims manual, sign-in, real payments, customer messages."

## Glossary

- **Claim**: a customer's request for payment under a policy: story, items claimed with amounts, supporting documents (as text), claim type, incident date and place.
- **Queue**: the 25 claims in `data/claims.json`, in record order (claim id); each shows its submitted date.
- **Policy**: one trip's cover: plan (Economy, Premium, First), add-ons, purchase date, trip dates, trip cost, travelers.
- **Claim history**: the customer's earlier claims, each with date, type, one-line summary, outcome and amount paid.
- **Policy wording**: the contract in `data/policy_wording.md`, organised in numbered sections (1. Your plan … 12. Definitions).
- **Handler**: one of the three claims handlers in `data/handlers.json`.
- **Agent**: the UnderCover Agent, an AI that works one claim at a time.
- **Instructions**: the text that tells the agent how to work a claim, kept as one committed text file and served read-only.
- **Decision**: the agent's outcome for a claim: **approve** (with a payout), **decline** or **refer**, plus a short calculation, an explanation and the policy section(s) relied on.
- **Refer**: hand the claim to a person because it needs judgment or more information: a required document is missing, the facts or documents are unclear or contradictory, or the wording does not settle the case. When unsure, the agent refers.
- **Outcome label**: approve, decline or refer, shown next to the state of a decided or waiting-for-sign-off claim.
- **Payout**: the amount in US dollars the agent works out for an approved claim.
- **Approval limit**: $1,000.00 (`payout_approval_limit` in `data/company.json`).
- **Sign-off**: a handler's confirmation that an approved payout over the approval limit may be paid.
- **Payment**: a recorded (not real) transfer of the payout for a claim.
- **Step**: one visible action of the agent while it works a claim: reading a record, reasoning text, recording a decision, attempting a payment, or an error.
- **Claim state**: exactly one of **waiting**, **in progress**, **waiting for sign-off**, **decided**.
- **Answer key**: the handlers' own decisions in `data/evals/`.
- **Run**: one attempt by the agent to work one claim, identified by a run (thread) id.
- **Operator**: the person running the pilot on their machine (the forward deployed engineer or a handler), who can start the agent, release a stuck claim or reset the data from the command line.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See the queue and each claim in full (Priority: P1)

A handler opens the dashboard and sees every claim in the queue with its state. They open a claim and see everything about it: the customer's story, the items and amounts, the documents, the policy, the customer's claim history and, once there is one, the agent's decision with its reasons.

**Why this priority**: Without the records and the screens, nothing else can be seen or checked. This is the base every other story stands on.

**Independent Test**: Load the business data, open the dashboard, check the 25 claims are listed as waiting, open one and compare what is shown with its record.

**Acceptance Scenarios**:

1. **Given** freshly loaded data, **When** a handler opens the dashboard, **Then** the queue lists all 25 claims from `data/claims.json` in claim id order, each with claim id, customer name, claim type, submitted date, amount claimed (as `$1,250.00`) and state `waiting`.
2. **Given** the queue, **When** the handler opens claim CLM-1001, **Then** they see its summary, full story, each item with category and amount, each document's name and text, the policy (plan, add-ons, purchase date, trip dates, trip cost, travelers), the customer's name and previous claims. Contact details (email, phone, address, date of birth) are not shown.
3. **Given** a claim with a decision, **When** the handler opens it, **Then** they see the outcome label, the payout (for approve), the calculation, the explanation and the policy section(s) cited.
4. **Given** the queue, **When** claims are in different states, **Then** each state is shown with its own label and colour, and decided claims also show their outcome label, so each of the four states and each of the three outcomes has its own distinct label.
5. **Given** a claim id that does not exist, **When** it is requested, **Then** the handler sees a "claim not found" message rather than a broken page.

---

### User Story 2 - The agent decides a claim (Priority: P1)

The agent takes a waiting claim, reads the claim, the customer's policy and claim history, and the policy wording, then approves, declines or refers it. On approval it works out the payout. It explains its decision in two or three sentences and names the relevant policy section. If the payout is within the approval limit, it pays; the claim is then decided.

**Why this priority**: This is the pilot's purpose: handling claims straight through the way a handler does.

**Independent Test**: With a scripted stand-in for the AI model, run the agent on one claim and check the claim ends with a recorded decision, explanation, cited section, payment (where due) and final state.

**Acceptance Scenarios**:

1. **Given** a waiting claim, **When** the agent starts on it, **Then** the claim's state becomes `in progress`.
2. **Given** the agent is working a claim, **When** it needs information, **Then** it obtains the claim, the policy, the customer's name and claim history, the policy wording and its own instructions only from the backend, and from nothing else. It never receives customer contact details.
3. **Given** the agent approves a claim with a payout of $1,000.00 or less, **When** it records the approval and pays, **Then** the approval and one payment for exactly that amount are recorded together and the claim becomes `decided`.
4. **Given** the agent declines or refers a claim, **When** the decision is recorded, **Then** the payout is $0.00, no payment is recorded and the claim becomes `decided`.
5. **Given** any recorded decision, **Then** it contains an outcome (approve, decline or refer), a payout, a short calculation, a non-empty explanation of at most 600 characters (the instructions ask for two or three sentences, and the scripted tests check it) and at least one cited policy section number and title that exist in the policy wording.
6. **Given** a claim that is already decided or waiting for sign-off, **When** the agent is started on it again, **Then** no second decision or payment is recorded.
7. **Given** the agent fails part-way (the AI model or the backend errors) before the claim reaches `decided` or `waiting for sign-off`, **Then** the error appears as a step, any unpaid decision is discarded, no payment exists and the claim returns to `waiting`; the steps of the failed run are kept.
8. **Given** a run is killed and leaves a claim `in progress` with no decision, **When** an operator releases that claim from the command line, **Then** the claim returns to `waiting` with an error step.
9. **Given** the agent works the whole queue, **When** one claim fails, **Then** the run continues with the next waiting claim, in queue order, and ends with a summary that lists the failed claims.

---

### User Story 3 - Payouts over $1,000 wait for a handler's sign-off (Priority: P1)

When the agent approves a payout over $1,000.00, the payment waits until a handler signs off. The system blocks the payment until then, even if the agent tries to pay. A handler opens the claim, reviews the decision and signs off; the payment is then made and the claim is decided.

**Why this priority**: A hard business rule from the head of claims. Money must never move over the limit without a person.

**Independent Test**: Record an approval over $1,000.00, attempt payment without sign-off (refused), sign off as a handler, check one payment is recorded.

**Acceptance Scenarios**:

1. **Given** the agent approves a claim with a payout of $1,000.01 or more, **When** the decision is recorded, **Then** the claim becomes `waiting for sign-off` and no payment is recorded.
2. **Given** a claim waiting for sign-off, **When** a payment is attempted without a sign-off (by the agent or anyone else), **Then** the payment is refused with a reason naming the failed check and nothing is recorded as paid; when the attempt comes from an agent run, the refusal appears as a step and the claim stays `waiting for sign-off` (a refusal is not a failure).
3. **Given** a claim waiting for sign-off, **When** a handler chooses their name and signs off on the claim page, **Then** the sign-off (handler and time) and one payment for the approved payout are recorded together, through the same payment checks as any other payment, and the claim becomes `decided`.
4. **Given** a sign-off names a handler who is not one of the three handlers, or whose record does not allow approving over the limit, **Then** it is refused.
5. **Given** the agent's set of tools, **Then** it has no way to sign off, release or reset a claim.
6. **Given** a payout of exactly $1,000.00, **Then** no sign-off is needed.
7. **Given** any claim, **When** a payment is attempted for an amount different from the approved payout, for a claim that is not approved, or for a claim already paid, **Then** the payment is refused.
8. **Given** a claim that is not waiting for sign-off, **When** a sign-off is attempted, **Then** it is refused.

---

### User Story 4 - Watch the agent work, step by step (Priority: P2)

While the agent works a claim, a handler on that claim's page sees each step appear as it happens: which records it read, what it reasoned, the decision it recorded and any payment attempt. After the claim is done, the full list of steps stays on the claim's page.

**Why this priority**: The team needs to trust the agent; seeing its work is how they build that trust. The pilot still delivers decisions without it.

**Independent Test**: Run the scripted agent on a claim while the claim page is open and check the steps appear in order without reloading the page.

**Acceptance Scenarios**:

1. **Given** a handler has a claim page open, **When** the agent takes a step on that claim, **Then** the step appears on the page within 6 seconds, without reloading.
2. **Given** a finished claim, **When** a handler opens it, **Then** all its steps are listed in the order they happened, each with time and kind (read, reasoning, decision, payment, error).
3. **Given** the queue page is open, **When** a claim's state changes, **Then** the new state is shown within 6 seconds, without reloading.

---

### User Story 5 - Read the agent's instructions (Priority: P3)

A handler opens a page that shows the instructions the agent works from. They can read them but not change them.

**Why this priority**: Transparency for the team; changing instructions is a later build.

**Independent Test**: Open the instructions page and compare its text with the instructions the agent receives.

**Acceptance Scenarios**:

1. **Given** the dashboard, **When** a handler opens the instructions page, **Then** they see exactly the text the agent receives as its instructions.
2. **Given** the instructions page, **Then** there is no way to edit or save the instructions, and the backend offers no operation that changes them.

### Edge Cases

- A document is missing for the claimed benefit (wording section 11): the agent refers the claim.
- The incident falls outside the covered trip dates: decline citing section 9, except a delay on the way home that section 3 covers.
- The claim was submitted more than 90 days after the incident: refer citing section 11 (the wording sets the window but no consequence, so a person judges).
- A document gives amounts in another currency: the agent uses the USD amounts on the claim's items and never converts; if the dollar amount is not established, it refers.
- The customer has earlier claims: history is context only; rules found only in the claims manual (such as repeat claims or meals without receipts) are not applied; if history raises a doubt the wording cannot settle, the agent refers.
- An approved payout exceeds the amount claimed or the plan's maximum for the claimed benefit: the approval is refused.
- The payout works out to $0.00 after deductible and limits (e.g., a deductible larger than the eligible amount): an approval of $0.00 is refused; the agent must record a decline with the reason. The system never rewrites the agent's outcome.
- The agent proposes a payout with more than two decimal places or a negative amount: the decision is refused and the agent must record a valid one.
- The agent tries to record a decision outcome other than approve, decline or refer: refused.
- The agent stops without recording a decision: treated as a failure (User Story 2, scenario 7).
- Two runs of the agent start on the same claim at once: only one may hold it `in progress`; the second is refused.
- The system restarts: all work is kept. Data is loaded only into an empty store.
- An operator resets the data with an explicit command: every claim returns to `waiting`, and all decisions, steps, sign-offs and payments are cleared. Reset is not available from the dashboard or to the agent.
- A claim from the security set (`data/security/`) or the held-out set is not part of the queue.

## Requirements *(mandatory)*

### Functional Requirements

**Records**

- **FR-001**: The system MUST load the claims queue, policies, customers (with claim history), plans, handlers, company settings and the policy wording from `data/` and MUST NOT load anything from `data/evals/` or `data/security/`.
- **FR-002**: The data MUST be loaded only into an empty store, so a restart keeps all work. An explicit reset command MUST return the system to the starting state (all claims waiting, no decisions, steps, sign-offs or payments). Reset MUST NOT be available from the dashboard or to the agent.
- **FR-002a**: A release command MUST move a claim that is `in progress` with no decision back to `waiting`, adding an error step. It MUST NOT be available to the agent.
- **FR-003**: The system MUST provide each claim's full record, its policy, its customer's name and claim history and the policy wording to the dashboard and to the agent, and MUST NOT provide customer contact details (email, phone, address, date of birth) to either.

**Claim states**

- **FR-004**: Every claim MUST be in exactly one state: waiting, in progress, waiting for sign-off, decided. Allowed moves: waiting → in progress; in progress → decided; in progress → waiting for sign-off; in progress → waiting (after a failure or a release, only while no payment exists); waiting for sign-off → decided (after sign-off and payment). All other moves MUST be refused.

**Agent**

- **FR-005**: The agent MUST work one claim per run, identified by claim id and a run (thread) id, and MUST be able to work every waiting claim in the queue in one go: one at a time in queue order, continuing past a failed claim and ending with a summary of failures.
- **FR-006**: The agent MUST obtain claims, policies, claim history, policy wording and its instructions only through the backend. Its tools MUST be limited to reading those records, recording a decision and paying; it MUST have no tool to sign off, release or reset.
- **FR-007**: No component reachable by the agent MUST expose the answer key.
- **FR-008**: The agent MUST record exactly one decision per claim: outcome (approve, decline, refer), payout in US dollars exact to the cent (zero unless approve), a short calculation, an explanation (non-empty, at most 600 characters; the instructions ask for two or three sentences), and one or more cited policy wording sections that exist. Amounts with more than two decimals or below zero MUST be refused.
- **FR-009**: The agent MUST base decisions on the policy wording only (not the claims manual), following the refer and decline rules in the Glossary and Edge Cases. The instructions MUST state these rules and MUST NOT mention or paraphrase the answer key.
- **FR-010**: An approval MUST carry a payout greater than $0.00, no greater than the total amount claimed and no greater than the plan's maximum for the claimed benefit; otherwise it MUST be refused.
- **FR-011**: The agent MUST request payment for an approved payout through a separate payment operation that takes the amount. For a payout of $1,000.00 or less, the approval and its payment MUST be recorded together or not at all.
- **FR-012**: Every action of the agent on a claim (record read, reasoning text, decision recorded, payment attempt and result, error) MUST be stored as a step on that claim, in order, with a time and its run id. Steps MUST be kept when a run fails.

**Sign-off and payment**

- **FR-013**: There MUST be exactly one way to record a payment, and it MUST refuse unless the claim is approved, the amount equals the approved payout, the claim has not been paid before and, when the payout is over the approval limit, a handler has signed off.
- **FR-014**: An approval over the approval limit MUST put the claim in `waiting for sign-off`, with no payment.
- **FR-015**: A handler MUST be able to sign off a claim waiting for sign-off by choosing their name from the three handlers. The sign-off MUST record handler and time and pay through the FR-013 payment path, all together, then move the claim to decided. A sign-off MUST be refused for an unknown handler, a handler not allowed to approve over the limit, or a claim already signed off. This is a record of who signed, not authentication. Sign-off only releases the payment; changing the agent's decision is not part of the pilot, and the claim page says so.
- **FR-016**: Payments are records only; the system MUST NOT move real money.

**Dashboard**

- **FR-017**: The dashboard MUST show the queue in claim id order (claim id, customer, claim type, submitted date, amount claimed, state, and outcome label once decided or waiting for sign-off) and refresh states within 6 seconds of a change.
- **FR-018**: The dashboard MUST show each claim in full (User Story 1, scenario 2), its decision with reasons and cited sections, its sign-off and payment if any, and its steps, updating within 6 seconds while the agent works.
- **FR-019**: The dashboard MUST show the agent's instructions read-only.
- **FR-020**: The dashboard MUST follow `docs/BRAND.md` (fonts, colours, light and dark surfaces, tone) and show money as US dollars with two decimals (`$1,250.00`).
- **FR-021**: The dashboard MUST NOT require sign-in; everyone sees everything.

### Key Entities

- **Claim**: id, policy, customer, type, submission date, incident date and place, summary, story, items (description, category, amount), amount claimed, documents (name, type, text), state.
- **Policy**: id, customer, plan, add-ons, purchase date, channel sold through, trip (destination, departure, return, trip cost), travelers, status.
- **Customer**: id, name, contact details, customer since, previous claims (id, filed on, incident date, type, summary, outcome, amount paid).
- **Plan**: name, limits, waiting periods, per-item limit, deductible; add-ons.
- **Handler**: id, name, role, may approve over the limit.
- **Decision**: claim, outcome, payout, calculation, explanation, cited sections, time.
- **Step**: claim, run id, order, time, kind, content.
- **Sign-off**: claim, handler, time.
- **Payment**: claim, amount, time.
- **Instructions**: the agent's working text (read-only in this pilot).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After loading the data, all 25 claims appear in the queue as waiting, and none of the held-out, security or answer-key data is reachable from the dashboard or by the agent (0 occurrences).
- **SC-002**: With a scripted stand-in for the AI model, working the whole queue leaves all 25 claims decided or waiting for sign-off, each with a complete decision (outcome, payout, calculation, 2–3 sentence explanation, at least one valid cited section). With the real model, no claim is left in progress, and any failed claims are listed and can be worked again.
- **SC-003**: 0 payments over $1,000.00 are recorded without a handler's sign-off, in every test, including tests where the agent deliberately tries to pay.
- **SC-004**: No claim is ever paid twice, and no payment differs from its approved payout.
- **SC-005**: A handler can find any claim and read its decision and reasons within 30 seconds of opening the dashboard.
- **SC-006**: Agent steps and state changes appear on an open page within 6 seconds.
- **SC-007**: A handler can sign off a claim in 2 actions or fewer from the claim page.
- **SC-008**: The full project check (`npm run check`) passes with coverage at or above 80%, and no automated test calls a real AI model.

## Assumptions

- The agent is started from the command line to work the queue (or one claim); the dashboard watches. Starting the agent from the dashboard is not required.
- All three handlers may sign off over the limit today (`can_approve_over_limit` is true for all), but the flag is still checked. Without sign-in, the handler picks their name when signing off.
- Sign-off is approval of the payment only; a handler overriding, rejecting or reversing the agent's decision is not part of this pilot (open question for the head of claims).
- A referred claim is `decided` with outcome `refer`; the follow-up by a person is outside the pilot.
- The full policy wording (`policy_wording.md`) is used, not the short version.
- `data/knowledge.json` and `data/claims_manual.md` are not used in this pilot.
- Decision accuracy against the answer key is measured in a later build (evaluations); the pilot does not read `data/evals/`.
- The default AI model and the free alternative follow `docs/TECH_STACK.md`; tests always use a scripted stand-in.
- Single user machine, local use; no concurrency beyond the two-runs-on-one-claim case.
