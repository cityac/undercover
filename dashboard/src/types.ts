export type State =
  "waiting" | "in_progress" | "waiting_for_sign_off" | "decided";
export type Outcome = "approve" | "decline" | "refer";
export type StepKind = "read" | "reasoning" | "decision" | "payment" | "error";

export interface QueueRow {
  claim_id: string;
  customer_name: string;
  claim_type: string;
  submitted_on: string;
  amount_claimed: string;
  state: State;
  outcome: Outcome | null;
}

export interface Section {
  number: number;
  title: string;
}

export interface Decision {
  outcome: Outcome;
  payout: string;
  calculation: string;
  explanation: string;
  sections: Section[];
  decided_at: string;
}

export interface Claim {
  claim_id: string;
  policy_id: string;
  customer_id: string;
  customer_name: string;
  claim_type: string;
  submitted_on: string;
  incident_date: string;
  incident_location: string;
  summary: string;
  story: string;
  items: { description: string; category: string; amount: string }[];
  amount_claimed: string;
  documents: { name: string; type: string; content: string }[];
  state: State;
  decision: Decision | null;
  sign_off: {
    handler_id: string;
    handler_name: string;
    signed_at: string;
  } | null;
  payment: { amount: string; paid_at: string } | null;
}

export interface Policy {
  policy_id: string;
  plan: { name: string };
  add_ons: string[];
  purchased_on: string;
  destination: string;
  departs_on: string;
  returns_on: string;
  trip_cost: string;
  travelers: string[];
}

export interface Customer {
  customer_id: string;
  name: string;
  customer_since: string;
  previous_claims: {
    claim_id: string;
    filed_on: string;
    claim_type: string;
    summary: string;
    outcome: string;
    amount_paid: string;
  }[];
}

export interface Handler {
  handler_id: string;
  name: string;
  role: string;
  can_approve_over_limit: boolean;
}

export interface Step {
  id: number;
  run_id: string;
  kind: StepKind;
  content: string;
  created_at: string;
}
