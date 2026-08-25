import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: ".",
  timeout: 30_000,
  expect: { timeout: 10_000 },
  fullyParallel: false,
  reporter: [["list"], ["html", { outputFolder: "../../playwright-report", open: "never" }]],
  use: { baseURL: process.env.PLAYWRIGHT_BASE_URL || "http://localhost:3000", trace: "retain-on-failure" },
  webServer: process.env.PLAYWRIGHT_BASE_URL ? undefined : [
    {
      command: "python -m uvicorn backend.app.main:app --port 8000",
      url: "http://127.0.0.1:8000/api/v1/health",
      cwd: "../..",
      reuseExistingServer: true,
    },
    {
      command: "pnpm --dir frontend dev",
      url: "http://127.0.0.1:3000",
      cwd: "../..",
      reuseExistingServer: true,
      env: { NEXT_PUBLIC_API_BASE_URL: "http://127.0.0.1:8000" },
    },
  ],
  projects: [
    { name: "desktop-chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "mobile-chromium", use: { ...devices["Pixel 7"] } },
  ],
});
