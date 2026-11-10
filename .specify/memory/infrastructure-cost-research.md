# Infrastructure Cost Notes

No market research was run: the infrastructure is set by the course briefs. Source: `AGENTS.md`,
`guides/for_agents/AGENT_GUIDE_*.md`.

| Stage | Infra | Cost |
|-------|-------|------|
| W1 (pilot, harness) | Local: FastAPI + SQLite, Vite | $0 |
| W2 (durable onward) | Supabase free plan (pauses after a week idle), Langfuse Cloud Hobby | $0 |
| W3 (secure → copilot) | AWS: Lambda, AgentCore Gateway/Runtime | Pay-as-you-go; run each lab's teardown, watch with `uv run monitor.py` |
| W3 free route | Render free web services in place of AWS | $0 |

Decision point: before W3D2, choose AWS or Render. Never create or delete AWS resources unless the student asks.
