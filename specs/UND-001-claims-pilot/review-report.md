# Code Review: UND-001 Claims pilot

## Summary
- Overall: WARN (pipeline continues)
- Checks: 5/7 PASS, 2/7 WARN, 0/7 FAIL
- Constitutions loaded: `.specify/memory/constitution.md`, `.specify/memory/autonomous-constitution.md`. No app-specific constitution applies (single app repo; the portfolio table does not apply).
- Base: `main...feature/UND-001-claims-pilot`, 69 files, +4355/−78
- Evidence: `npm run check` green. 66 Python tests at 98.84% coverage, 15 vitest tests at 99.23% statements, 8 Playwright tests on an isolated backend (:8001, `e2e/e2e.db`) and dashboard (:5174).

## Check Results
| Check | Score | Notes |
|-------|-------|-------|
| Spec Compliance | PASS | FR-001..021 and FR-002a are implemented. US1–US5 are covered by unit and e2e tests. |
| Constitution | PASS | I: STATUS.md is updated. II: the code is minimal, with no extra layers. III: a stub model is used and coverage is ≥80%, with no lowered thresholds and no disabled rules. IV: no `data/evals` reference in backend, agent or dashboard, and the seed SOURCES list is explicit. V: payment, the cap and sign-off are enforced in `backend/claims.py`, not in the prompt. |
| Pattern Consistency | PASS | It follows the skeleton conventions: `uv run -m`, an `operation_id` and docstring on every route, Readonly props, and strict TS with no `any`. |
| Error Handling | WARN | Four one-shot dashboard fetches have no `.catch` (see below). |
| Security | PASS | All SQL is parameterised (no f-string SQL). React escapes all text. `execFileSync` uses fixed args and an absolute `uv` path. There are no secrets in the diff; the key is read from env. Customer contact fields are not exposed. |
| Scope Creep | WARN | `CLAUDE.md` (2 lines from `update-agent-context.sh`) and `dashboard/index.html` (fonts) are not named as files in tasks.md, but both are expected by-products. |
| Prior Lessons | PASS | No `lessons.jsonl` yet. |

## Issues Found

### WARN: Error Handling
- **Files**:
  - `dashboard/src/components/SignOffPanel.tsx:13`
  - `dashboard/src/pages/InstructionsPage.tsx:7`
  - `dashboard/src/pages/ClaimDetails.tsx:47-48`
- **Issue**: `void api.x().then(...)` has no rejection handler. If the backend is down, the panel stays on "Loading" or shows an empty handler list, with an unhandled rejection in the console. The polled views (queue, claim, steps) do surface errors.
- **Suggestion**: Route these through `usePolling`, or add a `.catch` that shows a message. This is low impact for a local pilot.

### WARN: Scope Creep
- **Files**: `CLAUDE.md`, `dashboard/index.html`
- **Issue**: These files are not listed by path in tasks.md. The first was changed by the Spec Kit agent-context script. The second loads the Google Fonts required by T011 / BRAND.md.
- **Suggestion**: None needed.

### Note: bug found and fixed during e2e
`backend/db.py`: FastAPI ran the sync dependency and the endpoint in different threads, so `sqlite3` refused the connection and returned 500s under concurrent polling. The fix is `check_same_thread=False`, with one connection per request, plus a regression test in `test_db.py`. Worth recording as a lesson.

## Files Reviewed
- backend: `claims.py`, `db.py`, `main.py`, `models.py`, `money.py`, `release.py`, `seed.py`, `instructions.md`, and `tests/*`
- agent: `main.py`, `__main__.py`, and `tests/*`
- dashboard: `src/**`, `index.html`, `vite.config.ts`
- e2e: `*.spec.ts`, `helpers.ts`, plus `playwright.config.ts`
- `docs/STATUS.md`, `.gitignore`, `CLAUDE.md`
