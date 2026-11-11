import { money, summarize } from "../format";
import type { QueueRow } from "../types";
import { StateBadge } from "./Badges";

export function QueueSummary({ rows }: Readonly<{ rows: QueueRow[] }>) {
  return (
    <ul className="summary" aria-label="Queue summary">
      {summarize(rows).map(({ state, count, total }) => (
        <li key={state} className="summary-card" data-state={state}>
          <StateBadge state={state} />
          <span className="summary-count">
            {count} {count === 1 ? "claim" : "claims"}
          </span>
          <span className="summary-total mono">{money(total)}</span>
        </li>
      ))}
    </ul>
  );
}
