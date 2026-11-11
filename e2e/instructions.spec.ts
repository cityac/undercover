import { expect, test } from "@playwright/test";

test("the agent's instructions are shown read only", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("link", { name: "Agent instructions" }).click();
  await expect(page.getByText(/# UnderCover Agent instructions/)).toBeVisible();
  await expect(page.getByRole("textbox")).toHaveCount(0);
  await expect(page.getByRole("button")).toHaveCount(0);
});
