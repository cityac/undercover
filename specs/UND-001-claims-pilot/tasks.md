# Tasks: Claims Pilot (UND-001)

**Input**: `specs/UND-001-claims-pilot/` — plan.md, spec.md, research.md, data-model.md, contracts/api.md
**Tests**: REQUIRED (constitution III): every task that adds code adds its tests; no test calls a real model.
**Commits**: one commit per phase after its checkpoint passes (pre-commit hook runs; never `--no-verify`). Update `docs/STATUS.md` at each checkpoint.

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Setup

- [X] T001 Add `.gitignore` entries for `e2e/e2e.db*` and `undercover.db-*` (journal files) in `.gitignore`
- [X] T002 [P] Add `backend/tests/conftest.py` with a `db_path` fixture (temp file, sets `UNDERCOVER_DB` via monkeypatch) and a `client` fixture (seeded `TestClient`)

**Checkpoint 1**: `uv run pytest -q` passes (existing tests unchanged).

---

## Phase 2: Foundational

- [X] T003 Create `backend/money.py`: `to_cents(Decimal|str) -> int` (refuse >2 decimals / negative with `ValueError`), `to_str(cents) -> "0.00"`; tests in `backend/tests/test_money.py`
- [X] T004 Create `backend/db.py`: `db_path()` from `UNDERCOVER_DB` (default `undercover.db`), `connect()` (row factory, foreign keys), `create_schema(conn)` for every table in data-model.md, `is_empty(conn)`; tests in `backend/tests/test_db.py`
- [X] T005 Create `backend/seed.py`: `seed(conn)` loads exactly `claims.json, policies.json, customers.json, plans.json, handlers.json, company.json, policy_wording.md` (amounts → cents, sections parsed from `## N. Title`, claims `state='waiting'`, `seq` = file order); `reset()` drops and recreates; `__main__` runs `reset()` and prints a one-line summary; tests in `backend/tests/test_seed.py` (25 claims waiting, 12 sections, counts per table, the module's file list contains no `evals`, `security`, `claims_manual` or `knowledge`)
- [X] T006 Update `backend/main.py`: lifespan creates the schema and seeds only when empty; keep `/api/health`; test in `backend/tests/test_db.py` that a restart keeps an inserted step

**Checkpoint 2**: `uv run -m backend.seed` prints 25 claims; `uv run pytest -q` green; commit "Foundation: SQLite store, seed and reset".

---

## Phase 3: User Story 1 — Queue and claim in full (P1) 🎯 MVP

**Goal**: handlers see the 25 claims and each claim in full.
**Independent test**: seed, open dashboard, 25 waiting rows; open CLM-1001 and compare with its record.

- [X] T007 [US1] Create `backend/models.py` response models: `QueueRow`, `Claim` (with nullable `decision`, `sign_off`, `payment`), `Item`, `Document`, `Policy` (+ plan details), `Customer` (no contact fields), `Section`, `PolicyWording`, `Handler`, `Step`
- [X] T008 [US1] Add read functions in `backend/claims.py` (`list_queue`, `get_claim`, `get_policy`, `get_customer`, `get_policy_wording`, `list_handlers`, `list_steps`) and routes in `backend/main.py` per contracts/api.md (operation_id + one-line docstring, 404 on unknown id); tests in `backend/tests/test_reads.py` (claim id order, amounts as `"420.00"`, customer has no `email`/`phone`/`address`/`date_of_birth`, 404s)
- [X] T009 [P] [US1] Create `dashboard/src/types.ts` (API types) and `dashboard/src/api.ts` (typed `getJson`/`postJson`, one function per route)
- [X] T010 [P] [US1] Create `dashboard/src/format.ts` (`money("1250.00") → "$1,250.00"`, dates, state and outcome labels, claim type labels); tests `dashboard/src/format.test.ts`
- [X] T011 [P] [US1] Create `dashboard/src/styles.css` with brand tokens from `docs/BRAND.md` (Instrument Sans/Serif, JetBrains Mono via Google Fonts link in `dashboard/index.html`; light/dark surfaces; state colours Sea Green/Marigold/Coral/Cerulean; rounded panels, no outlines)
- [X] T012 [US1] Create `dashboard/src/route.ts` (`useRoute()` over `location.hash`: queue, claim/:id, instructions) and update `dashboard/src/App.tsx` (header with nav, renders the page); update `dashboard/src/App.test.tsx`
- [X] T013 [P] [US1] Create `dashboard/src/components/StateBadge.tsx` and `OutcomeBadge.tsx` (distinct label + colour per state and outcome); tests `dashboard/src/components/badges.test.tsx`
- [X] T014 [US1] Create `dashboard/src/pages/QueuePage.tsx` (table: claim id link, customer, type, submitted, amount, state, outcome) ; tests `dashboard/src/pages/QueuePage.test.tsx` (mocked fetch)
- [X] T015 [US1] Create `dashboard/src/pages/ClaimPage.tsx` (summary, story, items, documents, policy, customer name + previous claims, "Claim not found" on 404) and `dashboard/src/components/DecisionPanel.tsx` (outcome, payout, calculation, explanation, cited sections, sign-off and payment if any); tests `dashboard/src/pages/ClaimPage.test.tsx`

**Checkpoint 3**: `npm run check:python` and `npm run check:ts` green; `curl localhost:8000/api/claims` returns 25 rows; Playwright MCP: queue shows 25 `Waiting` rows, CLM-1001 page shows its 3 items and documents; commit "US1: queue and claim pages".

---

## Phase 4: User Story 2 — The agent decides a claim (P1)

**Goal**: the agent works a claim through the API and the decision is recorded.
**Independent test**: stub model works CLM-1001 end to end; claim decided with payment.

- [X] T016 [US2] Add request models (`StartRequest`, `DecisionRequest` with `Decimal` payout, `PaymentRequest`, `FailRequest`, `StepRequest`) in `backend/models.py`
- [X] T017 [US2] Implement in `backend/claims.py`: `start(claim_id, run_id)` (waiting → in_progress, else `Refused`), `record_decision(...)` (all rules in data-model.md incl. benefit cap per research R6, $0 approve refused, 600-char limits, known sections; decline/refer → decided, approve > limit → waiting_for_sign_off, approve ≤ limit stays in_progress), `pay(claim_id, amount)` (single guarded path; success → decided), `fail(claim_id, run_id, error)` (no payment → delete decision, error step, waiting), `add_step(...)`; a `Refused` exception carries the failed check
- [X] T018 [US2] Add write routes `start_claim`, `record_decision`, `pay_claim`, `fail_claim`, `add_step` in `backend/main.py` (409 on `Refused`, 422 on bad input)
- [X] T019 [US2] Tests `backend/tests/test_claims.py`: every move and refusal in data-model.md (start twice refused; decision wrong run / not in progress / twice; payout over cap, over amount, 3 decimals, negative, $0 approve; unknown section; decline → decided payout 0; approve 1000.00 → in_progress then pay → decided; pay wrong amount / twice / not approved refused; fail after decision unpaid → waiting, decision gone, steps kept; fail after payment refused)
- [X] T020 [US2] Create `backend/instructions.md` (wording-only rules; refer: missing document per section 11, unclear/contradictory facts, unsettled wording, when unsure; decline: clear exclusion, outside trip dates per section 9 except section 3 return delays; filed > 90 days → refer citing 11; USD item amounts, no conversion; history is context only, manual rules not applied; workflow: read claim, policy, customer, wording → record_decision with calculation, 2–3 sentence explanation, section numbers → pay approved payout; over $1,000 the payment waits for sign-off). Add `get_instructions` route in `backend/main.py`; test in `backend/tests/test_reads.py` (text equals file; no word "evals")
- [X] T021 [US2] Rewrite `agent/main.py`: tools `get_claim`, `get_policy`, `get_customer`, `get_policy_wording`, `record_decision`, `pay_claim` (409/422 → refusal text); `TOOLS` list; `run(claim_id, thread_id, llm=None)`: start → fetch instructions as system prompt → stream agent updates, posting each AI text (`reasoning`), tool call (`read`/`decision`/`payment`) and tool result as steps → on exception or claim still `in_progress` at the end → `fail`; returns final claim state
- [X] T022 [US2] Create `agent/__main__.py`: no arg → work all waiting claims in queue order, continue past failures, print summary (decided / waiting for sign-off / failed ids); one arg → that claim
- [X] T023 [US2] Tests `agent/tests/test_agent.py`: tool names are exactly the allow-list (no sign_off/release/reset); stub run on CLM-1001 (approve ≤ limit → decided, one payment, steps in order with kinds); stub decline → decided; stub that raises → claim back to waiting, error step; stub that never pays → fail → waiting; model name test kept. Tests `agent/tests/test_queue.py`: queue run over 3 stub claims with one failure → summary lists it

**Checkpoint 4**: `npm run check:python` green with ≥ 80%; with the stub, scripted run over all 25 claims leaves none in progress (test); commit "US2: decision rules and the agent".

---

## Phase 5: User Story 3 — Sign-off over $1,000 (P1)

**Goal**: over-limit payouts wait for a handler; payment blocked until then.
**Independent test**: approval of 1500.00 → waiting for sign-off; pay refused; sign off → decided with payment.

- [X] T024 [US3] Implement `sign_off(claim_id, handler_id)` in `backend/claims.py` (waiting_for_sign_off; known handler with `can_approve_over_limit`; not signed before; records sign-off and calls `pay` in one transaction) and route `sign_off_claim` in `backend/main.py`
- [X] T025 [US3] Tests `backend/tests/test_sign_off.py`: approve 1000.01 → waiting_for_sign_off, no payment; pay without sign-off refused (claim unchanged); 1000.00 needs no sign-off; sign-off unknown handler / flag false (handler row patched) / twice / wrong state refused; sign-off → decided, payment equals payout
- [X] T026 [US3] Test in `agent/tests/test_agent.py`: stub agent approves 1500.00 then tries `pay_claim` → refusal is a `payment` step, claim stays waiting_for_sign_off, no payment, run not failed
- [X] T027 [US3] Create `dashboard/src/components/SignOffPanel.tsx` (handler select from `/api/handlers`, Sign off button, note "Sign-off releases the payment; it does not change the decision", error text on 409) and show it in `ClaimPage.tsx` when waiting for sign-off; tests `dashboard/src/components/SignOffPanel.test.tsx`

**Checkpoint 5**: Python and TS checks green; Playwright MCP: a claim set to waiting for sign-off via API shows the panel, sign-off in 2 actions moves it to Decided with payment; commit "US3: handler sign-off".

---

## Phase 6: User Story 4 — Live steps (P2)

**Goal**: steps and states update on open pages within 3 s.

- [X] T028 [US4] Create `dashboard/src/usePolling.ts` (fetch every 1000 ms while mounted, stop on unmount); tests `dashboard/src/usePolling.test.ts` (fake timers)
- [X] T029 [US4] Create `dashboard/src/components/StepList.tsx` (ordered, time, kind label, content) and use polling for the claim, its steps (`ClaimPage.tsx`) and the queue (`QueuePage.tsx`); tests `dashboard/src/components/StepList.test.tsx` and polling update tests in the page tests

**Checkpoint 6**: TS check green; Playwright MCP: with a claim page open, posting steps via API shows them within 3 s; commit "US4: live agent steps".

---

## Phase 7: User Story 5 — Read-only instructions (P3)

- [X] T030 [US5] Create `dashboard/src/pages/InstructionsPage.tsx` (pre-formatted text from `/api/instructions`, no edit controls) and nav link; tests `dashboard/src/pages/InstructionsPage.test.tsx`
- [X] T031 [US5] Test in `backend/tests/test_reads.py` that no route other than GET exists for `/api/instructions` and no reset/release route exists (inspect `app.routes`)

**Checkpoint 7**: checks green; Playwright MCP: `#/instructions` shows the text; commit "US5: instructions page".

---

## Phase 8: End-to-end, release command and polish

- [X] T032 Create `backend/release.py` (`release(claim_id)`: in_progress with no payment → waiting + error step; prints result; `__main__` takes the claim id); tests `backend/tests/test_release.py`
- [X] T033 Update `dashboard/vite.config.ts` proxy target to `process.env.API_URL ?? "http://127.0.0.1:8000"`; update `playwright.config.ts` webServers: backend `uv run -m uvicorn backend.main:app --port 8001` with `env: { UNDERCOVER_DB: "e2e/e2e.db" }`, dashboard `npx vite dashboard --port 5174 --strictPort` with `env: { API_URL: "http://127.0.0.1:8001" }`, `baseURL` 5174, `workers: 1`
- [X] T034 Create `e2e/helpers.ts` (`reset()` runs `uv run -m backend.seed` with `UNDERCOVER_DB=e2e/e2e.db` via `execFileSync` env; scripted agent: `start`, `decision`, `payment`, `steps` through `request`)
- [X] T035 [P] Create `e2e/queue.spec.ts` (25 rows, Waiting, money format, open CLM-1001 shows items/documents/policy, unknown id → Claim not found)
- [X] T036 [P] Create `e2e/decision.spec.ts` (scripted approve ≤ limit + pay → Decided, Approve badge, calculation, explanation, section titles; scripted decline/refer badges; steps appear live within 3 s)
- [X] T037 [P] Create `e2e/sign-off.spec.ts` (scripted approve 1500.00 → Waiting for sign-off; API pay refused; choose handler + Sign off → Decided with payment)
- [X] T038 [P] Create `e2e/instructions.spec.ts` (text visible, no textbox or save button); keep `e2e/health.spec.ts`
- [X] T039 Update `docs/STATUS.md` (what is built, how to run: dev, agent, release, seed, check) and `README`-level notes only if needed
- [X] T040 Run `npm run check`; fix until green without lowering thresholds or excluding files

**Checkpoint 8**: `npm run check` green (Python, TS, Playwright); commit "Pilot: end-to-end tests and status".

---

## Dependencies

Phase 1 → 2 → 3 (US1) → 4 (US2) → 5 (US3) → 6 (US4) → 7 (US5) → 8. US3 needs US2's decision/payment rules; US4 needs US1 pages and US2 steps; US5 needs T020's route.

## Parallel examples

- Phase 3: T009, T010, T011, T013 (different files) after T008.
- Phase 8: T035–T038 after T034.

## Implementation strategy

MVP = Phases 1–5 (records, screens, agent, sign-off rule). Phases 6–7 add transparency; Phase 8 proves it end to end.
