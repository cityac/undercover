# Quickstart — UND-001 Claims Pilot

```bash
uv sync && npm install          # once
npm run dev                     # backend :8000 + dashboard http://localhost:5173 (seeds on first start)
uv run -m agent                 # work the whole queue (needs OPENROUTER_API_KEY, or MODEL_NAME=openrouter/free)
uv run -m agent CLM-1001        # work one claim
uv run -m backend.release CLM-1001   # free a claim stuck in progress
uv run -m backend.seed          # reset everything to the starting queue
npm run check                   # every check (no real model is called)
```

Validation walk-through:
1. Open the dashboard: 25 claims, all `Waiting`.
2. Open a claim, run `uv run -m agent <id>` in a terminal: steps appear on the page; the state moves to `Decided` or `Waiting for sign-off`.
3. For a claim waiting for sign-off, choose a handler and sign off: a payment appears and the claim is `Decided`.
4. `#/instructions` shows the agent's instructions, read-only.
