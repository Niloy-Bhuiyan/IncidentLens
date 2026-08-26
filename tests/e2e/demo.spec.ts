import { expect, test } from "@playwright/test";

test("demo investigation exposes evidence, timeline, evaluation, architecture, and 404", async ({ page }) => {
  await page.route("**/api/v1/investigations", async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 350));
    await route.continue();
  });
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /your app broke after a deployment/i })).toBeVisible();
  await page.getByRole("link", { name: /investigate demo incident/i }).first().click();
  await expect(page.getByText(/reading incident evidence/i)).toBeVisible();
  await expect(page.getByText(/three-letter currency codes/i)).toBeVisible();
  await expect(page.getByRole("heading", { name: /why this conclusion is credible/i })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Incident timeline" })).toBeVisible();

  await page.getByRole("button", { name: /shows the normalization change/i }).click();
  await expect(page.getByRole("link", { name: /open full source/i })).toBeVisible();
  await page.getByRole("link", { name: /open full source/i }).click();
  await expect(page.getByText(/source content/i)).toBeVisible();

  await page.goto("/evaluation");
  await expect(page.getByRole("heading", { name: /top-5 retrieval quality/i })).toBeVisible();
  await expect(page.getByText("Full pipeline", { exact: true })).toBeVisible();

  await page.goto("/under-the-hood");
  await expect(page.getByRole("heading", { name: /what runs. where it runs/i })).toBeVisible();
  await expect(page.getByRole("heading", { name: /real vectors. in-process store/i })).toBeVisible();

  await page.goto("/architecture");
  await expect(page.getByRole("heading", { name: /langgraph, node by node/i })).toBeVisible();

  await page.goto("/route-that-does-not-exist");
  await expect(page.getByRole("heading", { name: /this trail ends here/i })).toBeVisible();
});

test("demo API failure leaves a retryable state", async ({ page }) => {
  await page.route("**/api/v1/investigations", (route) => route.fulfill({
    status: 503,
    contentType: "application/json",
    body: JSON.stringify({
      error: { code: "provider_unavailable", message: "Demo temporarily unavailable", request_id: "e2e-request" },
    }),
  }));

  await page.goto("/investigations/demo");

  await expect(page.locator("section.errorState[role='alert']")).toContainText("Demo temporarily unavailable");
  await expect(page.getByRole("button", { name: /rebuild from the demo evidence/i })).toBeEnabled();
});

