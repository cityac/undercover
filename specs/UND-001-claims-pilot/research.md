# Research — UND-001 Claims Pilot

The stack is fixed by `docs/TECH_STACK.md` (FastAPI + SQLite, LangChain `create_agent` on OpenRouter, React + Vite + TypeScript, Playwright). The decisions below fill the gaps.

### R1. SQLite access: standard library `sqlite3`
- **Decision**: Use Python's `sqlite3` with a small `backend/db.py` (connect, schema, transactions). No ORM.
- **Rationale**: About ten tables of simple rows; `sqlite3` has no extra dependency (SQLAlchemy is only in the `server` group) and keeps the code short (constitution II). Transactions (`with conn:`) give the atomic sign-off+payment and decision+state moves.
- **Alternatives**: SQLAlchemy / SQLModel — more code and a dependency for no gain at this size.

### R2. Database location and test isolation
- **Decision**: The path comes from the `UNDERCOVER_DB` environment variable, default `undercover.db` at the repo root (already gitignored by `*.db`). Tests use a temporary file per test via a fixture. Playwright starts its own backend on port 8001 with `UNDERCOVER_DB=e2e/e2e.db`, set through the `webServer.env` option, which works on Windows.
- **Rationale**: Tests never touch the student's working data; no shell-specific env syntax.

### R3. Seeding, reset and release
- **Decision**: On startup the backend creates the schema and seeds from `data/` only if the store is empty. `uv run -m backend.seed` resets (drops all work, reseeds). `uv run -m backend.release CLM-xxxx` releases a stuck claim. Both write straight to the database and have no API route.
- **Rationale**: Restart keeps work (FR-002). The agent reaches only the HTTP API, so reset and release are out of its reach by construction (FR-002a, FR-006).
- **Seed sources**: `claims.json`, `policies.json`, `customers.json`, `plans.json`, `handlers.json`, `company.json`, `policy_wording.md`. Never `data/evals/`, `data/security/`, `claims_manual.md`, `knowledge.json`. A test asserts the seed module names no other path.

### R4. Money
- **Decision**: Store amounts as integer cents. The API accepts and returns amounts as decimal strings with two places (`"1250.00"`), modelled as `Decimal` in Pydantic. More than two decimal places or a negative value → 422. Comparisons use cents: over the limit means `payout_cents > 100000`.
- **Rationale**: Exact to the cent, no float drift on `$1,000.00` vs `$1,000.01`.
- **Alternatives**: Floats (drift); integer cents in the API (the agent's model would have to compute cents, which invites errors).

### R5. Policy sections
- **Decision**: The backend parses `## N. Title` headings from `policy_wording.md` at seed time into a `policy_sections` table. A decision cites a list of section numbers; the backend refuses unknown numbers. The dashboard shows "Section 3, Trip Delay".
- **Rationale**: The decision cites a number and title that exist, and the check is mechanical.

### R6. Benefit cap for approvals
- **Decision**: `claim_type` → plan field: `trip_cancellation` and `trip_interruption` → `min(trip_cancellation_max, trip_cost)`; `trip_delay` → `trip_delay_max`; `baggage_delay` → `baggage_delay_max`; `baggage` → `baggage_max`; `passport` → `passport_max`; `emergency_medical` → `emergency_medical_max`. The approval cap is `min(amount_claimed, benefit cap)`.
- **Rationale**: Wording section 1 and section 2 (lower of trip cost or maximum). Add-ons only change per-item limits (section 8), not benefit maximums, so they don't affect the cap. The exact calculation stays with the agent.

### R7. Claim state machine and atomicity
- **Decision**: `waiting → in_progress` via `start` (refused if not waiting; this is the lock against two runs). `record_decision` is accepted only `in_progress` and only once per run:
  - decline / refer → `decided` immediately (payout 0);
  - approve over the limit → `waiting_for_sign_off`;
  - approve within the limit → stays `in_progress` until `pay` succeeds, then `decided`.
  
  `fail` (from the agent's run loop on an exception, or when the run ends with the claim still `in_progress`) deletes an unpaid decision and moves `in_progress → waiting`. Sign-off and payment run in one transaction.
- **Rationale**: Implements "approval and payment together or not at all" without the agent needing a combined operation, while keeping payment a separate operation that takes the amount (TECH_STACK).

### R8. Agent steps and live view
- **Decision**: `run()` streams the LangGraph agent (`stream_mode="updates"`) and posts each AI text, tool call and tool result as a step to `POST /api/claims/{id}/steps`, with the run id. Step kinds: `read`, `reasoning`, `decision`, `payment`, `error`. The run loop does this; it is not a tool the model can call. The dashboard polls the claim and its steps every second while the page is open.
- **Rationale**: Every agent action is recorded in order, including refused payments (they come back as tool results). Polling at 1 s meets the 3-second target with no websocket or SSE code.
- **Alternatives**: Server-sent events — more code, still no sign-in; LangChain callbacks — harder to order and test than the stream.

### R9. Agent tools (allow-list)
- **Decision**: `get_claim`, `get_policy`, `get_customer` (name + previous claims), `get_policy_wording`, `record_decision`, `pay_claim`. Instructions are fetched by `run()` from `GET /api/instructions` and used as the system prompt. Start, fail and steps are called by `run()`, not by the model. No sign-off, release or reset anywhere in `agent/`. A test asserts the tool names.
- **Rationale**: FR-006, decision "Agent tool allow-list".

### R10. Instructions
- **Decision**: `backend/instructions.md`, committed, served by `GET /api/instructions` (read-only, no write route). It states the wording-only rules, refer/decline rules, USD-only rule, the 2–3 sentence explanation, the calculation line, section citations and the payment rule, and never mentions the answer key.

### R11. Personal data
- **Decision**: `GET /api/customers/{id}` returns `customer_id`, `name`, `customer_since`, `previous_claims` only. Contact fields are stored (seeded) but never serialised.

### R12. Dashboard routing and data
- **Decision**: Hash routes (`#/`, `#/claims/CLM-1001`, `#/instructions`) in a tiny `useRoute` hook; `fetch` wrappers in `api.ts`; no router or state library. Fonts from Google Fonts per `docs/BRAND.md`; colours as CSS variables with light and dark (`prefers-color-scheme`).
- **Rationale**: Three pages; adding react-router would be more code than the router.

### R13. Testing
- **Decision**: pytest with FastAPI `TestClient` against a temp DB; the agent tested with `GenericFakeChatModel` (stub that ignores `bind_tools`, as in the skeleton) and the backend client monkeypatched to `TestClient`. Vitest + Testing Library for components with mocked `fetch`. Playwright drives the API as a scripted agent (start → decision → payment / sign-off) and checks the screens.
- **Rationale**: Constitution III — no test calls a real model.

### R14. Queue command
- **Decision**: `uv run -m agent` works every waiting claim in order and prints a summary (decided, waiting for sign-off, failed). `uv run -m agent CLM-1001` works one claim. Run id = `run-<claim>-<timestamp>`.
