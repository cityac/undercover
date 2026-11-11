import { expect, test } from "@playwright/test";
import { ScriptedAgent, reset } from "./helpers";

test.beforeEach(() => {
  reset();
});

test("a payout over $1,000 waits for a handler's sign-off", async ({
  page,
  request,
}) => {
  const agent = new ScriptedAgent(request, "CLM-1003");
  await agent.start();
  await agent.decide({ outcome: "approve", payout: "1500.00", sections: [7] });
  const refused = await agent.pay("1500.00");
  expect(refused.status()).toBe(409);
  await page.goto("/#/claims/CLM-1003");
  await expect(page.getByText("Waiting for sign-off").first()).toBeVisible();
  await page.getByLabel("Handler").selectOption({ label: "Dana Whitfield" });
  await page.getByRole("button", { name: "Sign off and pay" }).click();
  await expect(page.getByText("Decided", { exact: true })).toBeVisible({
    timeout: 3000,
  });
  await expect(page.getByText(/Signed off by Dana Whitfield/)).toBeVisible();
  await expect(page.getByText(/Paid \$1,500\.00/)).toBeVisible();
});
