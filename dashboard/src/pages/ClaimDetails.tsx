import { useEffect, useState } from "react";
import { api } from "../api";
import { claimType, date, money } from "../format";
import type { Claim, Customer, Policy } from "../types";

export function ClaimDetails({ claim }: Readonly<{ claim: Claim }>) {
  return (
    <section className="panel" aria-label="Claim">
      <h2>{claim.summary}</h2>
      <p className="muted">
        {claimType(claim.claim_type)} · {claim.incident_location} · incident{" "}
        {date(claim.incident_date)} · submitted {date(claim.submitted_on)}
      </p>
      <h3>The customer's story</h3>
      <p>{claim.story}</p>
      <h3>Items claimed</h3>
      <table>
        <tbody>
          {claim.items.map((item) => (
            <tr key={item.description}>
              <td>{item.description}</td>
              <td>{item.category}</td>
              <td className="amount">{money(item.amount)}</td>
            </tr>
          ))}
          <tr>
            <th colSpan={2}>Total claimed</th>
            <td className="amount">{money(claim.amount_claimed)}</td>
          </tr>
        </tbody>
      </table>
      <h3>Documents</h3>
      {claim.documents.map((doc) => (
        <div key={doc.name}>
          <h4>{doc.name}</h4>
          <p className="document">{doc.content}</p>
        </div>
      ))}
    </section>
  );
}

export function PolicyPanel({ claim }: Readonly<{ claim: Claim }>) {
  const [policy, setPolicy] = useState<Policy | null>(null);
  const [customer, setCustomer] = useState<Customer | null>(null);
  useEffect(() => {
    void api.policy(claim.policy_id).then(setPolicy);
    void api.customer(claim.customer_id).then(setCustomer);
  }, [claim.policy_id, claim.customer_id]);
  return (
    <section className="panel" aria-label="Policy and history">
      <h2>Policy</h2>
      {policy && (
        <dl>
          <dt>Policy</dt>
          <dd className="id">{policy.policy_id}</dd>
          <dt>Plan</dt>
          <dd>{policy.plan.name}</dd>
          <dt>Add-ons</dt>
          <dd>
            {policy.add_ons.length
              ? policy.add_ons.map(claimType).join(", ")
              : "None"}
          </dd>
          <dt>Bought</dt>
          <dd>{date(policy.purchased_on)}</dd>
          <dt>Trip</dt>
          <dd>
            {policy.destination}, {date(policy.departs_on)} to{" "}
            {date(policy.returns_on)}
          </dd>
          <dt>Trip cost</dt>
          <dd className="mono">{money(policy.trip_cost)}</dd>
          <dt>Travelers</dt>
          <dd>{policy.travelers.join(", ")}</dd>
        </dl>
      )}
      <h2>{customer ? customer.name : "Customer"}</h2>
      {customer?.previous_claims.length === 0 && (
        <p className="muted">No earlier claims.</p>
      )}
      {customer && customer.previous_claims.length > 0 && (
        <ul>
          {customer.previous_claims.map((p) => (
            <li key={p.claim_id}>
              {date(p.filed_on)}: {p.summary} ({p.outcome},{" "}
              {money(p.amount_paid)})
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
