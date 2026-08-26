import { chromium } from "@playwright/test";

const baseUrl = process.env.PLAYWRIGHT_BASE_URL || "https://incidentlens-nine.vercel.app";
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();
const responses = [];
const consoleMessages = [];

page.on("response", (response) => {
  if (response.url().includes("incidentlens")) {
    responses.push({
      status: response.status(),
      method: response.request().method(),
      url: response.url(),
    });
  }
});
page.on("console", (message) => {
  if (["error", "warning"].includes(message.type())) {
    consoleMessages.push({ type: message.type(), text: message.text() });
  }
});

try {
  await page.goto(baseUrl, { waitUntil: "networkidle" });
  await page.getByRole("link", { name: /Investigate Demo Incident/ }).first().click();
  await page.getByText(/three-letter currency codes/).waitFor();
  const failed = responses.filter((response) => response.status >= 400);
  const report = {
    baseUrl,
    failed,
    api: responses.filter((response) => response.url.includes("incidentlens-api-delta")),
    consoleMessages,
  };
  console.log(JSON.stringify(report, null, 2));
  if (failed.length || consoleMessages.length) process.exitCode = 1;
} finally {
  await browser.close();
}
