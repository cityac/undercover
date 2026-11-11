import { expect, test } from "@playwright/test";
import { API } from "../playwright.config";

test("the backend is up and the dashboard loads", async ({ page, request }) => {
  const health = await request.get(`${API}/api/health`);
  expect(await health.json()).toEqual({ status: "ok" });
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "UnderCover Claims" }),
  ).toBeVisible();
});
