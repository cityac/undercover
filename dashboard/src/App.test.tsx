import { act, cleanup, render, screen } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { App } from "./App";
import { parse } from "./route";
import { claimRoutes, claim, mockApi, row } from "./testing";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  window.location.hash = "";
});

it("parses routes", () => {
  expect(parse("")).toEqual({ page: "queue" });
  expect(parse("#/claims/CLM-1001")).toEqual({ page: "claim", id: "CLM-1001" });
  expect(parse("#/instructions")).toEqual({ page: "instructions" });
  expect(parse("#/nowhere")).toEqual({ page: "queue" });
});

it("routes between pages", async () => {
  mockApi({
    "/api/claims": [row],
    "/api/instructions": { text: "Decide." },
    ...claimRoutes(claim),
  });
  render(<App />);
  expect(await screen.findByText("Claims queue")).toBeDefined();
  act(() => {
    window.location.hash = "#/instructions";
    window.dispatchEvent(new HashChangeEvent("hashchange"));
  });
  expect(await screen.findByText("Decide.")).toBeDefined();
  act(() => {
    window.location.hash = "#/claims/CLM-1001";
    window.dispatchEvent(new HashChangeEvent("hashchange"));
  });
  expect(await screen.findByText("Flight home canceled")).toBeDefined();
});
