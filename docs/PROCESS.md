# Process

`uv sync` and `npm install` at the repo root install everything, including a git pre-commit hook. `npm run dev` starts the backend and the dashboard.

`npm run check` runs every check:

- Python: ruff (lint and format), pyright, and pytest with 80% coverage
- TypeScript: ESLint, Prettier, tsc, and vitest with 80% coverage
- Playwright end-to-end tests

The pre-commit hook runs the format, lint, type and unit test checks on every commit.

## Workflow: Product Owner + Spec Kit

We plan and build with spec-driven development: `/productowner` decides what to build next, Spec Kit (`/speckit.*`, configured in `.specify/`) decides how. The governing rules are in `.specify/memory/constitution.md`.

Each build day is one Spec Kit feature, in `specs/NNN-<name>/` on a branch of the same name. The pilot works from `docs/SPEC.md`; every later day works from the brief copied into `docs/` (such as `docs/HARNESS.md`).

| Step | Command | Output |
|---|---|---|
| Pick the feature | `/productowner next --controlled` | the build day and its scope |
| Specify | `/speckit.specify <the brief>` | `spec.md`: user stories and acceptance criteria, traced to the brief |
| Clarify | `/speckit.clarify` | open questions settled in `spec.md` |
| Plan | `/speckit.plan` | `plan.md`, `research.md`, `data-model.md`, `contracts/` |
| Tasks | `/speckit.tasks` | `tasks.md` in phases |
| Check | `/speckit.analyze` | consistency of spec, plan and tasks |
| Implement | `/speckit.implement` | the code, phase by phase |
| Review | `/speckit.review` | review report |
| Document | `/productowner doc` | roadmap, PO state, `docs/STATUS.md` |

`/productowner next` (or `/speckit.pipeline <the brief> --scope L --commit`) runs every step without stopping.

## Planning

Planning means `spec.md`, `plan.md` and `tasks.md`, and no code.

- `tasks.md` splits the work into phases, usually 5 or 6, each building on the last.
- Every phase ends with a checkpoint of detailed success criteria that you can verify yourself: tests that pass, commands and their output, API calls and their responses, and pages you check in the browser with the Playwright MCP server. Write each one as a checkbox.
- In the step-by-step flow, stop after `/speckit.analyze` so the student can review the plan.

## Implementing

`/speckit.implement` builds every phase in order without stopping. For each phase:

1. Build it, with tests.
2. Check every success criterion and fix whatever fails.
3. Tick off its tasks and criteria in `tasks.md` and update `docs/STATUS.md`.
4. Commit. The pre-commit hook runs the checks; if it fails, fix the problem and commit again.

When the last phase is done, run `npm run check` and report the results.

## Rules

- Add tests with each change. Tests never call a model; use a stub model.
- Outside a plan, commit each change once you have checked it.
- Run `npm run check` before you hand work over.
- Never use `git commit --no-verify`.
- Never lower a threshold, turn off a rule or exclude a file to get a green run. If a rule looks wrong, stop and ask.
- Keep `docs/STATUS.md` up to date.
- Push only to `origin`, the student's fork. Pull requests go into the fork's `main`, never into `ed-donner/undercover`.
- Don't open `data/evals/` unless you're asked to.
- Everything must work on Windows: write `package.json` scripts as `uv run` commands or `.mjs` files.
