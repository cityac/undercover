import { act, cleanup, render, screen } from "@testing-library/react";
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
  expect(screen.getByText("$420.00")).toBeDefined();
  expect(screen.getByText("$3,800.00")).toBeDefined();
  expect(screen.getByText("Waiting")).toBeDefined();
  expect(screen.getByText("Decided")).toBeDefined();
  expect(screen.getByText("Refer")).toBeDefined();
  expect(screen.getAllByText("Trip delay")).toHaveLength(2);
  expect(
    screen.getByRole("link", { name: "CLM-1001" }).getAttribute("href"),
  ).toBe("#/claims/CLM-1001");
});

it("refreshes states while open", async () => {
  vi.useFakeTimers({ shouldAdvanceTime: true });
  const fetchMock = mockApi({ "/api/claims": [row] });
  render(<QueuePage />);
  expect(await screen.findByText("Waiting")).toBeDefined();
  mockApi({ "/api/claims": [{ ...row, state: "in_progress" }] });
  await act(async () => {
    await vi.advanceTimersByTimeAsync(POLL_MS);
  });
  expect(await screen.findByText("In progress")).toBeDefined();
  expect(fetchMock).toHaveBeenCalled();
});

it("shows an error when the backend is down", async () => {
  vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));
  render(<QueuePage />);
  expect(await screen.findByText("offline")).toBeDefined();
});
