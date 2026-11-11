import { act, cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { mockApi, row } from "../testing";
import { POLL_MS } from "../usePolling";
import { QueuePage } from "./QueuePage";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.useRealTimers();
});

it("lists the queue with states and outcomes", async () => {
  mockApi({
    "/api/claims": [
      row,
      {
        ...row,
        claim_id: "CLM-1003",
        amount_claimed: "3800.00",
        state: "decided",
        outcome: "refer",
      },
    ],
  });
  render(<QueuePage />);
  expect(await screen.findByText("CLM-1001")).toBeDefined();
  const table = within(screen.getByRole("table"));
  expect(table.getByText("$420.00")).toBeDefined();
  expect(table.getByText("$3,800.00")).toBeDefined();
  expect(table.getByText("Waiting")).toBeDefined();
  expect(table.getByText("Decided")).toBeDefined();
  expect(table.getByText("Refer")).toBeDefined();
  expect(table.getAllByText("Trip delay")).toHaveLength(2);
  expect(
    screen.getByRole("link", { name: "CLM-1001" }).getAttribute("href"),
  ).toBe("#/claims/CLM-1001");
});

it("refreshes states while open", async () => {
  vi.useFakeTimers({ shouldAdvanceTime: true });
  const fetchMock = mockApi({ "/api/claims": [row] });
  render(<QueuePage />);
  const table = within(await screen.findByRole("table"));
  expect(table.getByText("Waiting")).toBeDefined();
  mockApi({ "/api/claims": [{ ...row, state: "in_progress" }] });
  await act(async () => {
    await vi.advanceTimersByTimeAsync(POLL_MS);
  });
  expect(await table.findByText("In progress")).toBeDefined();
  expect(
    screen.getByText("1 claim", { selector: "[data-state=in_progress] *" }),
  ).toBeDefined();
  expect(fetchMock).toHaveBeenCalled();
});

it("shows an error when the backend is down", async () => {
  vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));
  render(<QueuePage />);
  expect(await screen.findByText("offline")).toBeDefined();
});

it("sums claims and amounts by state above the table", async () => {
  mockApi({
    "/api/claims": [
      row,
      { ...row, claim_id: "CLM-1002", amount_claimed: "80.50" },
      {
        ...row,
        claim_id: "CLM-1003",
        amount_claimed: "3800.00",
        state: "waiting_for_sign_off",
      },
    ],
  });
  render(<QueuePage />);
  const summary = await screen.findByRole("list", { name: "Queue summary" });
  const cards = within(summary).getAllByRole("listitem");
  expect(cards.map((card) => card.textContent)).toEqual([
    "Waiting2 claims$500.50",
    "In progress0 claims$0.00",
    "Waiting for sign-off1 claim$3,800.00",
    "Decided0 claims$0.00",
  ]);
});
