import { outcomeLabel, stateLabel } from "../format";
import type { Outcome, State } from "../types";

export function StateBadge({ state }: Readonly<{ state: State }>) {
  return <span className={`badge ${state}`}>{stateLabel[state]}</span>;
}

export function OutcomeBadge({ outcome }: Readonly<{ outcome: Outcome }>) {
  return <span className={`badge ${outcome}`}>{outcomeLabel[outcome]}</span>;
}
