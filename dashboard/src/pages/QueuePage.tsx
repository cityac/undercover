import { claimType, date, money } from "../format";
import { OutcomeBadge, StateBadge } from "../components/Badges";
import { QueueSummary } from "../components/QueueSummary";
import type { QueueRow } from "../types";
import { usePolling } from "../usePolling";

export function QueuePage() {
  const { data: rows, error } = usePolling<QueueRow[]>("/claims");
  if (!rows)
    return (
      <p className={error ? "error" : "muted"}>
        {error ? error.message : "Loading the queue"}
      </p>
    );
  return (
    <section className="panel">
      <h2>Claims queue</h2>
      <QueueSummary rows={rows} />
      <table>
        <thead>
          <tr>
            <th>Claim</th>
            <th>Customer</th>
            <th>Type</th>
            <th>Submitted</th>
            <th>Amount claimed</th>
            <th>State</th>
            <th>Outcome</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.claim_id}>
              <td className="id">
                <a href={`#/claims/${row.claim_id}`}>{row.claim_id}</a>
              </td>
              <td>{row.customer_name}</td>
              <td>{claimType(row.claim_type)}</td>
              <td>{date(row.submitted_on)}</td>
              <td className="amount">{money(row.amount_claimed)}</td>
              <td>
                <StateBadge state={row.state} />
              </td>
              <td>{row.outcome && <OutcomeBadge outcome={row.outcome} />}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
