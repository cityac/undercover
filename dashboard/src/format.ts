import type { Outcome, State, StepKind } from "./types";

const dollars = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
});

export function money(amount: string): string {
  return dollars.format(Number(amount));
}

export function date(iso: string): string {
  return new Date(
    iso.length === 10 ? `${iso}T00:00:00` : iso,
  ).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function time(iso: string): string {
  return new Date(iso).toLocaleTimeString("en-US", { hour12: false });
}

export const stateLabel: Record<State, string> = {
  waiting: "Waiting",
  in_progress: "In progress",
  waiting_for_sign_off: "Waiting for sign-off",
  decided: "Decided",
};

export const outcomeLabel: Record<Outcome, string> = {
  approve: "Approve",
  decline: "Decline",
  refer: "Refer",
};

export const stepLabel: Record<StepKind, string> = {
  read: "Read",
  reasoning: "Reasoning",
  decision: "Decision",
  payment: "Payment",
  error: "Error",
};

export function claimType(type: string): string {
  const words = type.replaceAll("_", " ");
  return words.charAt(0).toUpperCase() + words.slice(1);
}
