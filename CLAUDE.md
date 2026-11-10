# UnderCover — Claude Code instructions

`AGENTS.md` (Ed's course instructions) applies in full, except for how builds are planned and
implemented: this project uses **Product Owner + Spec Kit** instead of "Please plan X in
docs/PLAN_X.md" / "Please implement the plan". Details: `docs/PROCESS.md`,
`docs/SDD_ADAPTATION.md`, `.specify/memory/constitution.md`.

## Product Owner

The Product Owner decides WHAT to build (one build day at a time); Spec Kit decides HOW.

### Key files

| File | Purpose |
|------|---------|
| `docs/SPEC.md`, `docs/<BRIEF>.md` | Customer requirements (source of every feature) |
| `docs/STATUS.md` | What is built and how to run it — update after every phase |
| `.specify/memory/constitution.md` | Governing principles |
| `.specify/memory/po-state.md` | PO state: priority, decisions, sessions |
| `.specify/memory/feature-roadmap.md` | 9 build-day features with statuses |
| `specs/NNN-<name>/` | Spec Kit artefacts per feature |

### First actions every session

1. Read the docs listed in `AGENTS.md` "Start here".
2. Read the top of `.specify/memory/po-state.md`.
3. If a new brief is in `docs/`, unlock its roadmap feature (LOCKED → PENDING).

### Feature workflow

`/productowner next --controlled` → `/speckit.specify` → `/speckit.clarify` → `/speckit.plan` →
`/speckit.tasks` → `/speckit.analyze` → (student review) → `/speckit.implement` →
`/speckit.review` → `/productowner doc`.
Autonomous: `/productowner next` (runs `/speckit.pipeline ... --scope L --commit`).

### Tech stack

FastAPI + SQLite, LangChain `create_agent` on OpenRouter, React + Vite + TypeScript, Playwright;
uv + Python 3.12, Node 26. See `docs/TECH_STACK.md`.

## Active Technologies
- Python 3.12 (uv), TypeScript strict on Node 26 + FastAPI, Pydantic 2, stdlib `sqlite3`, httpx, LangChain `create_agent` + `langchain-openai` (OpenRouter); React 19, Vite 8 (feature/UND-001-claims-pilot)
- SQLite file (`UNDERCOVER_DB`, default `undercover.db`); amounts in integer cents (feature/UND-001-claims-pilot)

- (none yet beyond the skeleton)

## Recent Changes

- 2026-11-10: Switched build workflow to PO + Spec Kit (`docs/SDD_ADAPTATION.md`).
