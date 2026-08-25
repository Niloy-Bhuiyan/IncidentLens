import { expect, test } from "@playwright/test";

test("demo investigation exposes evidence, timeline, evaluation, architecture, and 404", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /find the change behind the failure/i })).toBeVisible();
  await page.getByRole("link", { name: /investigate the demo/i }).first().click();
  await expect(page.getByText(/violated the payment-adapter contract/i)).toBeVisible();
  await expect(page.getByRole("heading", { name: "Evidence trail" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Incident timeline" })).toBeVisible();

  await page.getByRole("button", { name: /shows the normalization change/i }).click();
  await expect(page.getByRole("link", { name: /open full source/i })).toBeVisible();
  await page.getByRole("link", { name: /open full source/i }).click();
  await expect(page.getByText(/source content/i)).toBeVisible();

  await page.goto("/evaluation");
  await expect(page.getByRole("heading", { name: /top-5 retrieval quality/i })).toBeVisible();
  await expect(page.getByText("Full pipeline")).toBeVisible();

  await page.goto("/architecture");
  await expect(page.getByRole("heading", { name: /langgraph, node by node/i })).toBeVisible();

  await page.goto("/route-that-does-not-exist");
  await expect(page.getByRole("heading", { name: /this trail ends here/i })).toBeVisible();
});

