# Implementation Plan: Claims Pilot

**Branch**: `feature/UND-001-claims-pilot` | **Date**: 2026-11-10 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/UND-001-claims-pilot/spec.md`, customer brief `docs/SPEC.md`

## Summary

Turn the hello-world skeleton into the claims pilot: a FastAPI + SQLite backend seeded from `data/` that owns the claim state machine and every business rule (one guarded payment path, the $1,000 sign-off, atomic decision/payment), a LangChain agent that works claims through the API only and streams its steps back, and a React dashboard with the queue, the claim page (decision, sign-off, live steps) and the read-only instructions. Design choices are in [research.md](research.md); tables in [data-model.md](data-model.md); routes in [contracts/api.md](contracts/api.md).

## Technical Context

**Language/Version**: Python 3.12 (uv), TypeScript strict on Node 26
**Primary Dependencies**: FastAPI, Pydantic 2, stdlib `sqlite3`, httpx, LangChain `create_agent` + `langchain-openai` (OpenRouter); React 19, Vite 8
**Storage**: SQLite file (`UNDERCOVER_DB`, default `undercover.db`); amounts in integer cents
**Testing**: pytest + coverage ≥ 80% (TestClient, stub chat model), vitest + Testing Library ≥ 80%, Playwright e2e on isolated backend :8001 / dashboard :5174
**Target Platform**: local machine (macOS / Windows / Linux)
**Project Type**: web application (backend + dashboard) plus an agent CLI
**Performance Goals**: steps and state changes visible within 6 s (5 s polling)
**Constraints**: no real model in tests; agent reaches only the HTTP API; no data from `data/evals/`; Windows-safe scripts
**Scale/Scope**: 25 claims, 3 handlers, 1 operator

## Constitution Check

| Principle | Gate | Status |
|---|---|---|
| I. Customer docs are the truth | Every FR traces to `docs/SPEC.md`; nothing from later briefs (no Supabase, LangGraph graph, evals, sign-in) | PASS |
| II. Simplicity | stdlib sqlite3, hash routing, polling; no ORM, router, state library or push channel | PASS |
| III. Tested, never a real model | Stub model in agent tests; Playwright plays the agent through the API; 80% thresholds unchanged | PASS |
| IV. Agent never sees the answer key | Seeder reads a fixed file list (test asserts no `evals`); agent tools only call the API | PASS |
| V. Rules enforced by the system | State machine + single payment guard in the backend; agent has no sign-off tool (tested) | PASS |
| Tech constraints | `operation_id`, one-line docstring, no optional inputs on every route; payment is its own operation taking the amount | PASS |

Re-check after design: PASS (no violations; Complexity Tracking empty).

## Project Structure

### Documentation (this feature)

```text
specs/UND-001-claims-pilot/
├── spec.md, decisions.md, consensus-report.md, quality-report.md
├── plan.md, research.md, data-model.md, quickstart.md
├── contracts/api.md
└── tasks.md            # /speckit.tasks
```

### Source Code (repository root)

```text
backend/
├── main.py            # FastAPI app, routes (thin), startup seed-if-empty
├── db.py              # connect(), schema, transaction helper
├── seed.py            # load data/ → tables; `uv run -m backend.seed` resets
├── release.py         # `uv run -m backend.release CLM-xxxx`
├── claims.py          # state machine + rules: start, decide, pay, sign_off, fail, release
├── money.py           # cents ⇄ "0.00" strings
├── models.py          # Pydantic request/response models
├── instructions.md    # the agent's instructions (read-only)
└── tests/             # test_seed, test_reads, test_claims (rules), test_api, conftest (temp DB)

agent/
├── main.py            # tools (allow-list), model(), run(claim_id, thread_id), step streaming
├── __main__.py        # `uv run -m agent [CLM-xxxx]`, queue summary
└── tests/             # test_tools, test_run (stub model), test_queue

dashboard/src/
├── App.tsx            # layout + hash routes
├── route.ts           # useRoute hook
├── api.ts             # typed fetch wrappers
├── types.ts           # API types
├── format.ts          # money/date/label formatting
├── usePolling.ts      # 5 s polling hook
├── pages/QueuePage.tsx, ClaimPage.tsx, InstructionsPage.tsx
├── components/StateBadge.tsx, OutcomeBadge.tsx, DecisionPanel.tsx, SignOffPanel.tsx, StepList.tsx
├── styles.css         # brand tokens, light/dark
└── *.test.tsx         # vitest

e2e/
├── health.spec.ts (existing), queue.spec.ts, decision.spec.ts, sign-off.spec.ts, instructions.spec.ts
└── helpers.ts         # reset via seed, scripted agent through the API
```

**Structure Decision**: Keep the skeleton's `backend/`, `agent/`, `dashboard/`, `e2e/` layout. Business rules live in `backend/claims.py` so routes stay thin and the rules are unit-tested directly.

## Phases (each ends with a commit; checks in tasks.md)

1. **Foundation**: db, schema, money, seed/reset, seed-if-empty, test fixtures.
2. **Read API + queue/claim screens (US1)**: read routes, brand styles, queue page, claim page.
3. **Rules (US2 + US3 backend)**: start, decision, payment, sign-off, fail, steps, release; full rule tests.
4. **Agent (US2)**: instructions, tool allow-list, `run()` with step streaming, queue CLI.
5. **Sign-off, live steps, instructions (US3 UI, US4, US5)**: sign-off panel, polling, step list, instructions page.
6. **End-to-end + docs**: Playwright isolation and specs, `docs/STATUS.md`, `npm run check`.

## Complexity Tracking

None.
