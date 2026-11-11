import { execFileSync } from "node:child_process";
import { existsSync } from "node:fs";
import { delimiter, join } from "node:path";
import type { APIRequestContext } from "@playwright/test";
import { API, E2E_DB } from "../playwright.config";

function uv(): string {
  const name = process.platform === "win32" ? "uv.exe" : "uv";
  const dirs = (process.env.PATH ?? "").split(delimiter);
  const found = dirs
    .map((dir) => join(dir, name))
    .find((path) => existsSync(path));
  if (!found) throw new Error("uv is not on the PATH");
  return found;
}

export function reset(): void {
  execFileSync(uv(), ["run", "-m", "backend.seed"], {
    env: { ...process.env, UNDERCOVER_DB: E2E_DB },
  });
}

export interface Decision {
  outcome: "approve" | "decline" | "refer";
  payout: string;
  sections: number[];
}

export class ScriptedAgent {
  constructor(
    private readonly request: APIRequestContext,
    private readonly claimId: string,
    private readonly runId = `e2e-${claimId}`,
  ) {}

  async start() {
    return this.request.post(`${API}/api/claims/${this.claimId}/start`, {
      data: { run_id: this.runId },
    });
  }

  async step(kind: string, content: string) {
    return this.request.post(`${API}/api/claims/${this.claimId}/steps`, {
      data: { run_id: this.runId, kind, content },
    });
  }

  async decide(decision: Decision) {
    return this.request.post(`${API}/api/claims/${this.claimId}/decision`, {
      data: {
        run_id: this.runId,
        calculation: `Payout ${decision.payout}`,
        explanation: "The wording covers this loss. The documents support it.",
        ...decision,
      },
    });
  }

  async pay(amount: string) {
    return this.request.post(`${API}/api/claims/${this.claimId}/payment`, {
      data: { amount },
    });
  }
}
