# Implemented Features

## Stage 1 — UND-001 Claims pilot (2026-11-11, PR #2)

Spec: `specs/UND-001-claims-pilot/`. Brief: `docs/SPEC.md`.

- **Backend** (`backend/`): FastAPI + stdlib `sqlite3`, `UNDERCOVER_DB`. Seeds `data/` (never `data/evals/`) into an empty store. Amounts are integer cents in the DB and decimal strings in the API.
  - States: waiting → in_progress (start = lock) → waiting_for_sign_off / decided. `fail` and `release` return an unpaid claim to waiting.
  - Decision checks: outcome; approve > $0 and ≤ min(claimed, plan max; trip cost for cancellation/interruption); decline/refer $0; cited sections must exist; one decision per claim.
  - One payment path, `pay_in`. A payout over $1,000 is refused until a handler with `can_approve_over_limit` signs off; sign-off pays in the same transaction.
  - Endpoints: `GET /api/health`, `/api/claims`, `/api/claims/{id}`, `/api/claims/{id}/steps`, `/api/policies/{id}`, `/api/customers/{id}`, `/api/policy-wording`, `/api/handlers`, `/api/instructions`; `POST /api/claims/{id}/start|decision|payment|sign-off|fail|steps`.
  - CLI: `uv run -m backend.seed` (reset), `uv run -m backend.release CLM-xxxx`.
- **Agent** (`agent/`): `run(claim_id, thread_id)` uses LangChain `create_agent` on OpenRouter (`MODEL_NAME`, default `openai/gpt-6-luna`). The system prompt is `backend/instructions.md`, read through the API. Tools are the claim, policy, customer and wording reads, `record_decision` (bound to the run) and `pay_claim`. Every step is posted to the backend. `uv run -m agent [ids]` works the queue and prints a summary.
- **Dashboard** (`dashboard/`): React 19 + Vite 8, hash routes. Pages: the queue with state and outcome badges; each claim in full with decision, calculation, cited sections, sign-off, payment, policy, history and live steps; the sign-off panel; the instructions, read only. It polls every 1 s and uses the BRAND.md tokens with light and dark themes.
- **Tests**: 66 pytest tests (98.84%, stub model), 15 vitest tests (99.23% of statements), 8 Playwright tests on an isolated :8001/:5174 with a scripted agent.

## Stage 2 — UND-002 Queue summary (2026-11-11)

- UND-002 Four cards under the Claims queue heading (`dashboard/src/components/QueueSummary.tsx`), in state order, each with the state badge, claim count and total amount claimed. Totals are summed in integer cents by `summarize()` in `format.ts`, from the same `GET /api/claims` data as the table.
