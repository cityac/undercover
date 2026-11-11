import { expect, test } from "@playwright/test";
import { reset } from "./helpers";

test.beforeEach(() => {
  reset();
});

test("the queue lists every claim as waiting", async ({ page }) => {
  await page.goto("/");
  const rows = page.locator("tbody tr");
  await expect(rows).toHaveCount(25);
  await expect(rows.first()).toContainText("CLM-1001");
  await expect(rows.first()).toContainText("Maya Patel");
  await expect(rows.first()).toContainText("$420.00");
  await expect(page.getByText("Waiting", { exact: true })).toHaveCount(25);
});

test("a claim opens in full", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("link", { name: "CLM-1001" }).click();
  await expect(
    page.getByRole("heading", { name: /Flight home canceled/ }),
  ).toBeVisible();
  await expect(page.getByText("Airport hotel, one night")).toBeVisible();
  await expect(
    page.getByText("Meridian Air cancellation notice"),
  ).toBeVisible();
  await expect(page.getByText("UnderCover Premium")).toBeVisible();
  await expect(
    page.getByText(/Checked bag arrived 30 hours late/),
  ).toBeVisible();
  await expect(page.getByText("maya.patel@example.com")).toHaveCount(0);
});

test("an unknown claim says so", async ({ page }) => {
  await page.goto("/#/claims/CLM-0000");
  await expect(page.getByText("Claim not found: CLM-0000")).toBeVisible();
});
