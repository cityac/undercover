import { defineConfig } from "@playwright/test";

export const API = "http://127.0.0.1:8001";
export const E2E_DB = "e2e/e2e.db";

export default defineConfig({
  testDir: "e2e",
  outputDir: "e2e/test-results",
  reporter: "list",
  workers: 1,
  use: { baseURL: "http://localhost:5174" },
  webServer: [
    {
      command: "uv run -m uvicorn backend.main:app --port 8001",
      url: `${API}/api/health`,
      env: { UNDERCOVER_DB: E2E_DB },
      reuseExistingServer: false,
    },
    {
      command: "npx vite dashboard --port 5174 --strictPort",
      url: "http://localhost:5174",
      env: { API_URL: API },
      reuseExistingServer: false,
    },
  ],
});
