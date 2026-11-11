import { vi } from "vitest";
import type { Claim, QueueRow } from "./types";

export type Routes = Record<string, unknown>;

export function mockApi(routes: Routes) {
  const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    const url = input instanceof Request ? input.url : input.toString();
    const key = `${init?.method ?? "GET"} ${url}`;
    const body = key in routes ? routes[key] : routes[url];
    if (body === undefined)
      return Promise.resolve(
        new Response(JSON.stringify({ detail: `${url} not found` }), {
          status: 404,
        }),
      );
    if (body instanceof Response) return Promise.resolve(body);
    return Promise.resolve(new Response(JSON.stringify(body)));
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

export const row: QueueRow = {
  claim_id: "CLM-1001",
  customer_name: "Maya Patel",
  claim_type: "trip_delay",
  submitted_on: "2026-06-24",
  amount_claimed: "420.00",
  state: "waiting",
  outcome: null,
};

export const claim: Claim = {
  claim_id: "CLM-1001",
  policy_id: "POL-2001",
  customer_id: "CUS-3001",
  customer_name: "Maya Patel",
  claim_type: "trip_delay",
  submitted_on: "2026-06-24",
  incident_date: "2026-06-18",
  incident_location: "Rome, Italy",
  summary: "Flight home canceled",
  story: "My flight home from Rome was canceled.",
  items: [
    {
      description: "Airport hotel",
      category: "accommodation",
      amount: "245.00",
    },
  ],
  amount_claimed: "420.00",
  documents: [
    { name: "Hotel receipt", type: "receipt", content: "Hotel Aurelia" },
  ],
  state: "waiting",
  decision: null,
  sign_off: null,
  payment: null,
};

export const policy = {
  policy_id: "POL-2001",
  plan: { name: "UnderCover Premium" },
  add_ons: ["electronics_plus"],
  purchased_on: "2026-04-22",
  destination: "Rome, Italy",
  departs_on: "2026-06-10",
  returns_on: "2026-06-18",
  trip_cost: "3100.00",
  travelers: ["Maya Patel"],
};

export const customer = {
  customer_id: "CUS-3001",
  name: "Maya Patel",
  customer_since: "2023-04-11",
  previous_claims: [
    {
      claim_id: "CLM-0412",
      filed_on: "2024-08-19",
      claim_type: "baggage_delay",
      summary: "Bag arrived 30 hours late",
      outcome: "approved",
      amount_paid: "140.00",
    },
  ],
};

export const claimRoutes = (c: Claim, steps: unknown[] = []): Routes => ({
  [`/api/claims/${c.claim_id}`]: c,
  [`/api/claims/${c.claim_id}/steps`]: steps,
  "/api/policies/POL-2001": policy,
  "/api/customers/CUS-3001": customer,
  "/api/handlers": [
    {
      handler_id: "HND-01",
      name: "Dana Whitfield",
      role: "Senior",
      can_approve_over_limit: true,
    },
    {
      handler_id: "HND-02",
      name: "Marcus Oyelaran",
      role: "Handler",
      can_approve_over_limit: false,
    },
  ],
});
