# Product Owner State

Last updated: 2026-11-10

## Current Priority

**NEXT ACTION**: Feature #1 — Claims pilot (W1D3), scope L
- **Why**: Only unlocked feature; `docs/SPEC.md` is its brief. Everything later builds on it.
- **After that**: #2 Agent harness, once `labs/week1day5_product_HARNESS.md` is copied to `docs/HARNESS.md`.
- **Command**: `/speckit.specify` with `docs/SPEC.md` as the description (controlled), or
  `/speckit.pipeline "Claims pilot per docs/SPEC.md" --scope L --commit` (autonomous).

## MVP Definition

Core hypothesis (`docs/SPEC.md`):
> "Can an AI agent handle claims straight through, as accurately as our handlers do?"

**MVP = Features needed to test this hypothesis:**
1. Claims pilot — PENDING

**MVP does NOT require**: claims manual, sign-in, real payments, customer messages ("Not for now" in `docs/SPEC.md`).

## Implementation Status

### Completed
- Skeleton: `GET /api/health`; agent `run(claim_id, thread_id)` with one health tool; one dashboard page; one e2e test; lefthook + `npm run check`.

### Not Yet Built
- All 9 roadmap features (1 PENDING, 8 LOCKED).

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

## Feature Log

- {feature_id: UND-001 (#1 pilot), scope: L, ts: 2026-11-10} — recommended

## Open Questions

- Commit `.specify/`, `.claude/commands/`, `CLAUDE.md` and the `docs/` changes to `main` of the fork?

## Risks Being Tracked

1. Untracked Spec Kit files lost on branch switch — commit them.
2. `data/evals/` leakage through specs or consensus prompts — constitution IV.
3. Week 3 AWS costs — teardown after every lab.
