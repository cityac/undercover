---
project_name: "Undercover"
project_acronym: "UND"
---

# UnderCover Constitution

UnderCover is the claims platform for UnderCover Travel Insurance (fictional), built across the
build days of Ed Donner's "AI FDE" course. The documents in `docs/` are the customer's
requirements; this constitution is how we build against them with Spec Kit.

## Core Principles

### I. The customer's documents are the source of truth

- `docs/SPEC.md` and each brief copied into `docs/` (`HARNESS.md`, `DURABLE.md`, ...) are the
  requirements. Every user story and acceptance criterion in a `spec.md` traces back to one of them.
- Before `/speckit.specify` or `/speckit.plan`, read in full: `docs/SPEC.md`, `docs/TECH_STACK.md`,
  `docs/CODE_STANDARDS.md`, `docs/PROCESS.md`, `docs/BRAND.md`, `docs/STATUS.md`, plus the brief
  for the feature.
- Build only what `docs/` asks for. A brief in `labs/` is not in scope until it is copied into
  `docs/`. Never build ahead for a later build day. Anything listed under "Not for now" stays out.
- Where a brief's notes on earlier builds don't match the code, follow the brief's intent.

### II. Simplicity (from `docs/CODE_STANDARDS.md`)

- Keep it simple, do not overcomplicate. YAGNI.
- Comments only when necessary. Short READMEs, no emojis.
- No overly defensive code. Handle exceptions only when necessary.
- Python: ALWAYS `uv run`, NEVER `python3`.
- TypeScript: strict mode, never `any`.

### III. Tested, never against a real model (NON-NEGOTIABLE)

- Every change ships with tests. Tests never call a model; use a stub model.
- Coverage stays at or above 80% for Python (pytest) and TypeScript (vitest).
- User-visible behavior has Playwright tests in `e2e/`. Acceptance criteria are written so that a
  test, a command's output, an API response or a Playwright check can verify them.
- Never lower a threshold, turn off a rule or exclude a file to get a green run. If a rule looks
  wrong, stop and ask.

### IV. The agent never sees the answer key (NON-NEGOTIABLE)

- `data/evals/` holds the handlers' decisions. No agent, prompt, tool, fixture or test reads it,
  and the coding agent does not open it unless the student asks.
- The UnderCover Agent reaches claims and its instructions only through the backend's API.
- Specs, decisions and consensus reviews must not quote or summarise `data/evals/`.

### V. Business rules are enforced by the system, not the prompt

- A payout over $1,000 needs a handler's sign-off. The backend blocks the payment until then, even
  if the agent tries to pay. Rules like this are enforced in code and covered by tests.
- Decisions follow the policy wording. Amounts are in US dollars.

## Technology Constraints

From `docs/TECH_STACK.md` (that file wins on any conflict):

- `backend/`: FastAPI + SQLite. Every operation has an `operation_id`, a one-line docstring and no
  optional inputs. Paying a claim is a separate operation that takes the amount.
- `agent/`: LangChain `create_agent` on OpenRouter; one entry point `run(claim_id, thread_id)`.
  Model `openai/gpt-6-luna` (low reasoning) unless `MODEL_NAME` is set.
- `dashboard/`: React + Vite + TypeScript, styled per `docs/BRAND.md`.
- `e2e/`: Playwright.
- Python 3.12 with uv in the root `pyproject.toml`; Node 26. Secrets live in `.env` only.
- Everything works on Windows: `package.json` scripts are `uv run` commands or `.mjs` files.
- Never create or delete AWS resources unless the student asks.

## Development Workflow

- One build day = one Spec Kit feature (`specs/NNN-<name>/`), driven by `/productowner` and
  `/speckit.*`. See `docs/PROCESS.md`.
- `tasks.md` is organised in phases that each build on the last, with a checkpoint per phase.
  Every checkpoint is verifiable by the agent itself (tests, command output, API calls, Playwright).
- Commit after each phase. The lefthook pre-commit hook runs format, lint, types and unit tests.
  Never `git commit --no-verify`.
- Run `npm run check` (Python + TypeScript + Playwright) before handing work over.
- Keep `docs/STATUS.md` up to date after every phase: what is built and how to run it.
- Git: push only to `origin` (the student's fork). PRs go into the fork's `main`, never into
  `ed-donner/undercover`.
- Ed's `upstream/week*-end` branches are reference implementations: do not read them while planning
  or while the work is going well. If stuck, read them and tell the student.

## Governance

- This constitution and `docs/` override generic Spec Kit defaults. On conflict between this file
  and `docs/`, `docs/` wins and this file gets amended.
- Amendments: edit this file, bump the version (MAJOR: principle removed or redefined; MINOR:
  principle or section added; PATCH: wording), record the change in `.specify/memory/po-state.md`.
- `/speckit.review` checks every feature against these principles.

**Version**: 1.0.0 | **Ratified**: 2026-11-10 | **Last Amended**: 2026-11-10
