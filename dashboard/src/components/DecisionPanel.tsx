import { date, money } from "../format";
import type { Claim } from "../types";
import { OutcomeBadge } from "./Badges";

export function DecisionPanel({ claim }: Readonly<{ claim: Claim }>) {
  const { decision, sign_off: signOff, payment } = claim;
  if (!decision)
    return (
      <section className="panel">
        <h2>Decision</h2>
        <p className="muted">The agent has not decided this claim yet.</p>
      </section>
    );
  return (
    <section className="panel" aria-label="Decision">
      <h2>
        Decision <OutcomeBadge outcome={decision.outcome} />
      </h2>
      {decision.outcome === "approve" && (
        <p>
          Payout <span className="mono">{money(decision.payout)}</span>
        </p>
      )}
      <p>{decision.explanation}</p>
      <p className="muted">Calculation: {decision.calculation}</p>
      <p>
        Policy wording:{" "}
        {decision.sections
          .map((s) => `Section ${String(s.number)}, ${s.title}`)
          .join("; ")}
      </p>
      {signOff && (
        <p>
          Signed off by {signOff.handler_name} on {date(signOff.signed_at)}
        </p>
      )}
      {payment && (
        <p>
          Paid <span className="mono">{money(payment.amount)}</span> on{" "}
          {date(payment.paid_at)}
        </p>
      )}
    </section>
  );
}
