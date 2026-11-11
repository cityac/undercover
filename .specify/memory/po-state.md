# Product Owner State

Last updated: 2026-11-11

## Current Priority

**NEXT ACTION**: Feature #2 — Agent harness (W1D5), LOCKED until its brief is in `docs/`
- **Why**: #1 Claims pilot is COMPLETE (PR #2 into the fork). #2 builds on it.
- **Unlock**: copy `labs/week1day5_product_HARNESS.md` to `docs/HARNESS.md` when the course reaches W1D5, then `/productowner next`.
- **Before that**: merge PR #2 (https://github.com/cityac/undercover/pull/2).

## MVP Definition

Core hypothesis (`docs/SPEC.md`):
> "Can an AI agent handle claims straight through, as accurately as our handlers do?"

**MVP = Features needed to test this hypothesis:**
1. Claims pilot — COMPLETE (accuracy vs handlers not measured yet; that comes with later features)

**MVP does NOT require**: claims manual, sign-in, real payments, customer messages ("Not for now" in `docs/SPEC.md`).

## Implementation Status

### Completed
- Skeleton: `GET /api/health`; agent `run(claim_id, thread_id)` with one health tool; one dashboard page; one e2e test; lefthook + `npm run check`.

- #1 Claims pilot (UND-001): backend rules + SQLite, agent with tool allow-list, dashboard, isolated e2e. See `docs/STATUS.md`.

### Not Yet Built
- 8 roadmap features (#2–#9), all LOCKED.

## Decision Log

| Date | Decision | Rationale | Alternatives Rejected |
|------|----------|-----------|----------------------|
| 2026-11-10 | Use PO + Spec Kit instead of Ed's "Please plan" → `docs/PLAN*.md` flow | Student's SDD workflow; docs remain customer requirements | Ed's PLAN.md flow |
| 2026-11-10 | One build day = one Spec Kit feature (`specs/NNN-<name>/`) | Keeps each build comparable with Ed's `-start`/`-end` branches | Splitting a day into many specs |
| 2026-11-10 | Features LOCKED until their brief is in `docs/` | Course rule: never build ahead | Full roadmap open |
| 2026-11-10 | `docs/PROCESS.md` rewritten for Spec Kit; other `docs/` files untouched | PROCESS is engineering process, the rest are customer requirements | Leaving PROCESS.md contradicting the workflow |
| 2026-11-10 | Push + PR allowed, only into `cityac/undercover` | Student's override of "Never push" | No push |
| 2026-11-10 | No cost-research subagents; cost notes taken from course guides | Stack and models are fixed by `docs/TECH_STACK.md`; course budgets ~$10 | Market price research |
| 2026-11-10 | `CLAUDE.md` created (did not exist); `AGENTS.md` left as Ed's | Avoid merge conflicts on `git pull upstream` | Editing AGENTS.md |

| 2026-11-11 | Pilot money in integer cents; one guarded payment path; sign-off pays in the same transaction | Rules enforced by the system (constitution V) | Agent-side limit checks |
| 2026-11-11 | E2E on an isolated backend :8001 / `e2e/e2e.db` and dashboard :5174 | Tests never touch the dev DB | Reusing :8000 |

| 2026-11-11 | Queue summary (UND-002) added outside the course briefs | Explicit student request; dashboard only, derived from `GET /api/claims` | New summary API |

## Feature Dependencies

```
#1 Pilot ──► #2 Harness ──► #3 Durable ──► #4 Swarm ──► #5 Improve ──► #6 Secure ──► #7 Context ──► #8 Runtime ──► #9 Copilot
```

## Session History

### Session 1 (2026-11-10) — Init
- Analysed `docs/` (Ed's flow for Claude Code / Codex / OpenCode via AGENTS.md).
- Filled constitution, fixed autonomous-constitution, filled e2e guide app structure, rewrote `docs/PROCESS.md`.
- Created roadmap (9 features), PO state, cost notes, `CLAUDE.md`, `docs/SDD_ADAPTATION.md`.

### Session 2 (2026-11-10) — next --controlled
- Recommended #1 Claims pilot, scope L. No new briefs in `docs/`, no `specs/` yet.
- Handed off to `/speckit.specify`.

### Session 3 (2026-11-10 → 2026-11-11) — next (autonomous)
- `/speckit.pipeline` for UND-001, scope L: spec, 5-agent consensus, quality gate, plan, 40 tasks, implement, e2e, review (5 PASS / 2 WARN / 0 FAIL).
- E2E caught an SQLite cross-thread bug (500s under polling); fixed with a regression test.
- PR #2 opened into `cityac/undercover` main.

### Session 4 (2026-11-11) — student request
- UND-002 Queue summary, scope S: four state cards with count and total over the queue table.
- Separate fix PR #3: 5 s polling; agent returns 404 to the model instead of failing.

## Feature Log

- {feature_id: UND-001 (#1 pilot), scope: L, ts: 2026-11-10} — recommended
- {feature_id: UND-001 (#1 pilot), scope: L, ts: 2026-11-11} — COMPLETE, PR #2
- {feature_id: UND-002 (queue summary), scope: S, ts: 2026-11-11} — COMPLETE

## Open Questions

- Fix the two review WARNs (dashboard one-shot fetches without `.catch`) in #2 or separately?

## Risks Being Tracked

1. Local Node is v22 by default; the project needs Node 26 (`nvm use 26`) or `npm install` fails on engines.
2. `data/evals/` leakage through specs or consensus prompts — constitution IV.
3. Week 3 AWS costs — teardown after every lab.
