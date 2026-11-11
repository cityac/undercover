import { expect, it } from "vitest";
import {
  claimType,
  date,
  money,
  outcomeLabel,
  stateLabel,
  stepLabel,
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
