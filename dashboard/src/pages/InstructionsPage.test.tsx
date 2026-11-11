import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { mockApi } from "../testing";
import { InstructionsPage } from "./InstructionsPage";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

it("shows the instructions read only", async () => {
  mockApi({ "/api/instructions": { text: "# UnderCover Agent instructions" } });
  render(<InstructionsPage />);
  expect(
    await screen.findByText("# UnderCover Agent instructions"),
  ).toBeDefined();
  expect(screen.queryByRole("textbox")).toBeNull();
  expect(screen.queryByRole("button")).toBeNull();
});
