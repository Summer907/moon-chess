import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./e2e",
  workers: 1,
  fullyParallel: false,
  use: { baseURL: "http://127.0.0.1:8018", locale: "zh-CN", trace: "retain-on-failure" },
  webServer: {
    command: "uv run --project .. uvicorn --app-dir ../backend app.main:app --host 127.0.0.1 --port 8018 --no-access-log",
    url: "http://127.0.0.1:8018/api/health",
    reuseExistingServer: false,
    env: {
      RATE_LIMIT_CREATE_PER_MINUTE: "10000", RATE_LIMIT_CREATE_PER_HOUR: "10000",
      RATE_LIMIT_GENERAL_PER_MINUTE: "10000", RATE_LIMIT_AI_PER_MINUTE: "10000",
      MAX_GAMES_PER_IP: "10000",
    },
  },
});
