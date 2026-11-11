import { expect, test } from "@playwright/test";
import { ScriptedAgent, reset } from "./helpers";

test.beforeEach(() => {
  reset();
});

test("an approval within the limit is paid and shown with its steps", async ({
  page,
  request,
}) => {
  await page.goto("/#/claims/CLM-1001");
  await expect(page.getByText("No steps yet.")).toBeVisible();
  const agent = new ScriptedAgent(request, "CLM-1001");
  await agent.start();
  await agent.step("read", "get_claim: CLM-1001");
  await expect(page.getByText("get_claim: CLM-1001")).toBeVisible({
    timeout: 7000,
  });
  await expect(page.getByText("In progress")).toBeVisible({ timeout: 7000 });
  await agent.decide({ outcome: "approve", payout: "420.00", sections: [3] });
  await agent.pay("420.00");
  await expect(page.getByText("Decided", { exact: true })).toBeVisible({
    timeout: 7000,
  });
  await expect(page.getByText("Approve", { exact: true })).toBeVisible();
  await expect(
    page.getByText("Policy wording: Section 3, Trip Delay"),
  ).toBeVisible();
  await expect(page.getByText(/Paid \$420\.00/)).toBeVisible();
});

test("declines and referrals carry their own labels in the queue", async ({
  page,
  request,
}) => {
  const decline = new ScriptedAgent(request, "CLM-1001");
  await decline.start();
  await decline.decide({ outcome: "decline", payout: "0.00", sections: [9] });
  const refer = new ScriptedAgent(request, "CLM-1002");
  await refer.start();
  await refer.decide({ outcome: "refer", payout: "0.00", sections: [11] });
  await page.goto("/");
  await expect(page.locator("tbody tr").nth(0)).toContainText("Decline");
  await expect(page.locator("tbody tr").nth(1)).toContainText("Refer");
});
