# UnderCover - Feature Roadmap

Source: `docs/SPEC.md` (pilot) and the build-day briefs listed in `AGENTS.md`. One feature = one
build day = one Spec Kit feature. A feature is **LOCKED** until its brief is copied from `labs/`
into `docs/` (course rule: never build ahead). Descriptions of locked features come from the
`AGENTS.md` table only; the briefs themselves are read when unlocked.

## Phase 1: Week 1 - AI Engineer
| # | Feature | Status | Description | Priority | Spec |
|---|---------|--------|-------------|----------|------|
| 1 | **Claims pilot** (W1D3) | PENDING | From `docs/SPEC.md`: FastAPI+SQLite backend seeded from `data/`; UnderCover Agent (`run(claim_id, thread_id)`) reads claim, policy, history and policy wording via API, approves/declines/refers, computes payout, explains in 2-3 sentences with the policy section; dashboard: queue with states (waiting, in progress, waiting for sign-off, decided), claim detail with decision and reasons, live agent steps, read-only agent instructions; payout > $1,000 blocked until handler sign-off | P1 | — |
| 2 | **Agent harness** (W1D5, `HARNESS.md`) | LOCKED | The agent's tools, middleware and instructions | P1 | — |

## Phase 2: Week 2 - AI Architect
| # | Feature | Status | Description | Priority | Spec |
|---|---------|--------|-------------|----------|------|
| 3 | **Durable state** (W2D3, `DURABLE.md`) | LOCKED | Supabase; the claim agent as a LangGraph graph | P1 | — |
| 4 | **Swarm + evals** (W2D4, `SWARM.md`) | LOCKED | A dispatcher with a swarm of claim agents, and evaluations | P1 | — |
| 5 | **Improve + sign-in** (W2D5, `IMPROVE.md`) | LOCKED | Versioned agent configuration, an improver agent, sign-in | P1 | — |

## Phase 3: Week 3 - AI FDE (production on AWS)
| # | Feature | Status | Description | Priority | Spec |
|---|---------|--------|-------------|----------|------|
| 6 | **Secure** (W3D2, `SECURE.md`) | LOCKED | Agent API key, hidden-instruction check, app ready for AWS Lambda | P1 | — |
| 7 | **Context layer** (W3D3, `CONTEXT.md`) | LOCKED | Context layer from `context/`, agent memory, AgentCore Gateway | P1 | — |
| 8 | **Runtime** (W3D4, `RUNTIME.md`) | LOCKED | Agent as AgentCore app on AgentCore Runtime; decisions sent back. Lab 1 first moves `runtime/`, `agentcore/` to repo root | P1 | — |
| 9 | **Copilot** (W3D5, `COPILOT.md`) | LOCKED | UnderCover Copilot: a chat for handlers in the dashboard | P1 | — |

<!-- Statuses: LOCKED (brief not in docs/) | PENDING | PARTIALLY | COMPLETE -->

## Dependencies

Strictly sequential: #1 → #2 → #3 → #4 → #5 → #6 → #7 → #8 → #9. Each brief builds on the product
as it stands (the student's build or Ed's `upstream/week*-start`).

---

## Key Metrics & Targets

| Metric | Target | Source |
|--------|--------|--------|
| Straight-through handling | Claims decided without a handler, as accurately as handlers | `docs/SPEC.md` "Our goal" |
| Decision + payout accuracy | Scored against `data/evals/` (never shown to the agent) | `docs/SPEC.md`, `data/README.md` |
| Sign-off rule | 0 payments > $1,000 without sign-off | `docs/SPEC.md` Rules |
| Code quality | `npm run check` green, coverage ≥ 80% | `docs/PROCESS.md` |
| Course API spend | ~$10 total; free route available | `AGENTS.md` |

## Competitive Landscape

Not applicable: internal tool for a fictional insurer. Baseline = 3 handlers working the queue by hand.

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Agent sees the answer key | Constitution IV; agent reaches data only through the API; nothing loads `data/evals/` |
| Prompt-only enforcement of the $1,000 rule | Constitution V: backend blocks payment; tests prove it |
| Drift from Ed's build breaks later briefs | Keep `docs/STATUS.md` current; compare with `upstream/week*-end` only when stuck |
| `.specify/`, `.claude/`, `specs/` untracked → lost on `git checkout upstream/...-start` | Commit them on a branch before any branch switch |
| Week 3 AWS spend | Run each lab's teardown; `uv run monitor.py`; Render as free route |
| Tests hitting a real model | Stub model in every test |

## Market Data

Not applicable (course project).
