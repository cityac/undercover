import { expect, it } from "vitest";
import {
  cents,
  claimType,
  date,
  fromCents,
  money,
  outcomeLabel,
  stateLabel,
  stepLabel,
  summarize,
  time,
} from "./format";

it("formats money as US dollars", () => {
  expect(money("1250.00")).toBe("$1,250.00");
  expect(money("0.00")).toBe("$0.00");
});

it("formats dates and times", () => {
  expect(date("2026-06-24")).toBe("Jun 24, 2026");
  expect(time("2026-06-24T10:05:03")).toBe("10:05:03");
});

it("labels states, outcomes, steps and claim types", () => {
  expect(stateLabel.waiting_for_sign_off).toBe("Waiting for sign-off");
  expect(outcomeLabel.refer).toBe("Refer");
  expect(stepLabel.error).toBe("Error");
  expect(claimType("trip_delay")).toBe("Trip delay");
});

it("sums amounts exactly in cents", () => {
  expect(cents("0.10") + cents("0.20")).toBe(30);
  expect(fromCents(30)).toBe("0.30");
  expect(fromCents(125000)).toBe("1250.00");
});

it("summarizes the queue by state in state order", () => {
  const summary = summarize([
    { state: "waiting", amount_claimed: "0.10" },
    { state: "waiting", amount_claimed: "0.20" },
    { state: "decided", amount_claimed: "3800.00" },
  ]);
  expect(summary).toEqual([
    { state: "waiting", count: 2, total: "0.30" },
    { state: "in_progress", count: 0, total: "0.00" },
    { state: "waiting_for_sign_off", count: 0, total: "0.00" },
    { state: "decided", count: 1, total: "3800.00" },
  ]);
});
