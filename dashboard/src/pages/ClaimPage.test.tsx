import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { claim, claimRoutes, customer, mockApi } from "../testing";
import type { Claim } from "../types";
import { ClaimPage } from "./ClaimPage";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

const decided: Claim = {
  ...claim,
  state: "decided",
  decision: {
    outcome: "approve",
    payout: "420.00",
    calculation: "245 + 95 + 80 = 420",
    explanation: "The flight was canceled. The costs are covered.",
    sections: [{ number: 3, title: "Trip Delay" }],
    decided_at: "2026-11-10T10:00:00+00:00",
  },
  payment: { amount: "420.00", paid_at: "2026-11-10T10:00:01+00:00" },
};

it("shows the claim in full", async () => {
  mockApi(claimRoutes(claim));
  render(<ClaimPage id="CLM-1001" />);
  expect(await screen.findByText("Flight home canceled")).toBeDefined();
  expect(
    screen.getByText("My flight home from Rome was canceled."),
  ).toBeDefined();
  expect(screen.getByText("Airport hotel")).toBeDefined();
  expect(screen.getByText("Hotel Aurelia")).toBeDefined();
  expect(
    screen.getByText("The agent has not decided this claim yet."),
  ).toBeDefined();
  expect(await screen.findByText("UnderCover Premium")).toBeDefined();
  expect(screen.getByText("Electronics plus")).toBeDefined();
  expect(await screen.findByText(/Bag arrived 30 hours late/)).toBeDefined();
  expect(screen.getByText("No steps yet.")).toBeDefined();
});

it("shows the decision, payment and steps", async () => {
  mockApi(
    claimRoutes(decided, [
      {
        id: 1,
        run_id: "r",
        kind: "read",
        content: "get_claim: {}",
        created_at: "2026-11-10T10:00:00",
      },
      {
        id: 2,
        run_id: "r",
        kind: "error",
        content: "boom",
        created_at: "2026-11-10T10:00:02",
      },
    ]),
  );
  render(<ClaimPage id="CLM-1001" />);
  expect(await screen.findByText("Approve")).toBeDefined();
  expect(
    screen.getByText("The flight was canceled. The costs are covered."),
  ).toBeDefined();
  expect(
    screen.getByText("Policy wording: Section 3, Trip Delay"),
  ).toBeDefined();
  expect(screen.getByText(/Calculation: 245/)).toBeDefined();
  expect(await screen.findByText("get_claim: {}")).toBeDefined();
  expect(screen.getByText("Error")).toBeDefined();
});

it("shows a customer with no earlier claims", async () => {
  mockApi({
    ...claimRoutes(claim),
    "/api/customers/CUS-3001": { ...customer, previous_claims: [] },
  });
  render(<ClaimPage id="CLM-1001" />);
  expect(await screen.findByText("No earlier claims.")).toBeDefined();
});

it("says when a claim is not found", async () => {
  mockApi({});
  render(<ClaimPage id="CLM-0000" />);
  expect(await screen.findByText("Claim not found: CLM-0000")).toBeDefined();
});

it("signs off a payout over the limit", async () => {
  const waiting: Claim = {
    ...decided,
    state: "waiting_for_sign_off",
    decision: decided.decision && { ...decided.decision, payout: "1500.00" },
    payment: null,
  };
  const fetchMock = mockApi({
    ...claimRoutes(waiting),
    "POST /api/claims/CLM-1001/sign-off": {
      ...waiting,
      state: "decided",
      sign_off: {
        handler_id: "HND-01",
        handler_name: "Dana Whitfield",
        signed_at: "2026-11-10T11:00:00",
      },
    },
  });
  render(<ClaimPage id="CLM-1001" />);
  expect(await screen.findByText("Waiting for sign-off")).toBeDefined();
  expect(screen.getByText(/does not change the decision/)).toBeDefined();
  await screen.findByRole("option", { name: "Dana Whitfield" });
  expect(screen.queryByRole("option", { name: "Marcus Oyelaran" })).toBeNull();
  const button = screen.getByRole("button", { name: "Sign off and pay" });
  expect((button as HTMLButtonElement).disabled).toBe(true);
  fireEvent.change(screen.getByLabelText(/Handler/), {
    target: { value: "HND-01" },
  });
  fireEvent.click(button);
  await waitFor(() => {
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/claims/CLM-1001/sign-off",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ handler_id: "HND-01" }),
      }),
    );
  });
});

it("shows a refused sign-off", async () => {
  const waiting: Claim = {
    ...decided,
    state: "waiting_for_sign_off",
    payment: null,
  };
  mockApi({
    ...claimRoutes(waiting),
    "POST /api/claims/CLM-1001/sign-off": new Response(
      JSON.stringify({ detail: "the claim has already been signed off" }),
      { status: 409 },
    ),
  });
  render(<ClaimPage id="CLM-1001" />);
  await screen.findByRole("option", { name: "Dana Whitfield" });
  fireEvent.change(screen.getByLabelText(/Handler/), {
    target: { value: "HND-01" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Sign off and pay" }));
  expect(
    await screen.findByText("the claim has already been signed off"),
  ).toBeDefined();
});
