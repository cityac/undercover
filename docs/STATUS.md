# Status

The claims pilot (UND-001, `specs/UND-001-claims-pilot/`) is built.

- `backend/`: FastAPI on SQLite (`UNDERCOVER_DB`, default `undercover.db`). It loads `data/` into an empty store on first start and keeps all work across restarts. It owns every rule: the claim states, the decision checks (outcome, payout cap, policy sections), the one guarded payment path, and the $1,000 sign-off. It never reads `data/evals/`.
- `backend/instructions.md`: the agent's instructions, served read only at `/api/instructions`.
- `agent/`: the UnderCover Agent, `run(claim_id, thread_id)`. Its tools read the claim, the policy, the customer's history and the wording, record a decision and pay. It has no tool to sign off, release or reset. Each step is recorded on the claim, and a failed run returns the claim to the queue.
- `dashboard/`: the queue with a summary per state (claim count and total amount claimed) and the states and outcomes, each claim in full (decision, calculation, cited sections, sign-off, payment, live agent steps), sign-off by a handler for payouts over $1,000, and the agent's instructions. It polls every 5 seconds.
- `e2e/`: Playwright on its own backend (port 8001, `e2e/e2e.db`) and dashboard (port 5174), with a scripted agent driving the API.

## How to run

| Command | What it does |
|---|---|
| `npm run dev` | Backend on :8000 and the dashboard at http://localhost:5173 |
| `uv run -m agent` | Work every waiting claim in order and print a summary |
| `uv run -m agent CLM-1001` | Work one claim |
| `uv run -m backend.release CLM-1001` | Free a claim left in progress by a run that died |
| `uv run -m backend.seed` | Reset: clear all work and reload the starting queue |
| `npm run check` | Every check; no test calls a real model |

The agent uses `OPENROUTER_API_KEY` and the model in `MODEL_NAME` (default `openai/gpt-6-luna`).

## Known limits of the pilot

- No sign-in. A handler picks their name to sign off; it is a record, not authentication.
- Sign-off only releases the payment. A handler cannot reject or change the agent's decision.
- Decision accuracy against the handlers' decisions is not measured yet.
