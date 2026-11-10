# AI API Cost Notes

No market research was run: the model is fixed by `docs/TECH_STACK.md`, and this is a course project
with no revenue model. The figures come from the course guides (`AGENTS.md`, `guides/for_agents/`).

| Item | Value |
|------|-------|
| Default model | `openai/gpt-6-luna`, low reasoning effort, via OpenRouter (`OPENROUTER_API_KEY`) |
| Free route | `MODEL_NAME=openrouter/free` (daily allowance; `tiny` eval subset of 5 claims fits in it) |
| Course budget | ~$10 of API spend for the whole course |
| Unit of work | One claim decision: claim + policy + history + policy wording (short enough for a prompt) |
| Dev/test cost | $0: tests always use a stub model (constitution III) |
| Main spend | Running the agent on the 25-claim queue and the eval runs (W2D4 onwards) |

Recommendation: develop with the stub; run the real model on the `tiny` subset first, then the full queue.
