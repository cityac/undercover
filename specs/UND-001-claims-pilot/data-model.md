# Data Model — UND-001 Claims Pilot

SQLite tables (`backend/db.py`). Amounts in integer cents (`*_cents`). JSON columns hold arrays as text.

## Seeded reference data (from `data/`)

| Table | Columns | Source |
|---|---|---|
| `company` | `key` PK, `value` (JSON) | `company.json` |
| `plans` | `plan` PK, `name`, `trip_cancellation_max_cents`, `trip_delay_waiting_hours`, `trip_delay_max_cents`, `baggage_delay_waiting_hours`, `baggage_delay_max_cents`, `baggage_max_cents`, `per_item_limit_cents`, `passport_max_cents`, `emergency_medical_max_cents`, `deductible_cents` | `plans.json` |
| `handlers` | `handler_id` PK, `name`, `role`, `can_approve_over_limit` (bool) | `handlers.json` (email not stored) |
| `customers` | `customer_id` PK, `name`, `email`, `phone`, `date_of_birth`, `address` (JSON), `customer_since`, `previous_claims` (JSON) | `customers.json` |
| `policies` | `policy_id` PK, `customer_id` FK, `plan` FK, `add_ons` (JSON), `purchased_on`, `sold_through`, `destination`, `departs_on`, `returns_on`, `trip_cost_cents`, `travelers` (JSON), `status` | `policies.json` |
| `policy_sections` | `number` PK, `title` | `## N. Title` headings of `policy_wording.md` |
| `documents` | `name` PK (`policy_wording`), `content` | `policy_wording.md` |
| `claims` | `claim_id` PK, `seq` (file order), `policy_id` FK, `customer_id` FK, `claim_type`, `submitted_on`, `incident_date`, `incident_location`, `summary`, `story`, `items` (JSON: description, category, amount_cents), `amount_claimed_cents`, `documents` (JSON), `state` | `claims.json`; `state` = `waiting` |

## Work records

| Table | Columns | Rules |
|---|---|---|
| `runs` | `run_id` PK, `claim_id` FK, `started_at` | created by `start` |
| `decisions` | `claim_id` PK/FK, `run_id`, `outcome` (`approve`/`decline`/`refer`), `payout_cents`, `calculation`, `explanation`, `sections` (JSON ints), `decided_at` | one per claim; deleted by `fail` if unpaid |
| `steps` | `id` PK autoinc, `claim_id` FK, `run_id`, `kind` (`read`/`reasoning`/`decision`/`payment`/`error`), `content`, `created_at` | append-only; kept on failure |
| `sign_offs` | `claim_id` PK/FK, `handler_id` FK, `signed_at` | one per claim |
| `payments` | `claim_id` PK/FK, `amount_cents`, `paid_at` | one per claim (PK enforces never twice) |

## Claim states

```
waiting ──start──► in_progress ──decision: decline/refer──────────────► decided
                       │  ──decision: approve ≤ $1,000 ──► (in_progress) ──pay──► decided
                       │  ──decision: approve > $1,000 ──► waiting_for_sign_off ──sign-off+pay──► decided
                       └──fail / release (no payment)──► waiting
```

## Validation rules

- `outcome` ∈ {approve, decline, refer}; decline/refer → `payout = 0.00`.
- approve → `0 < payout ≤ min(amount_claimed, benefit cap)` (research R6).
- `payout` ≥ 0, at most 2 decimals.
- `explanation` non-empty, ≤ 600 characters; `calculation` non-empty, ≤ 600 characters.
- `sections` non-empty; each number exists in `policy_sections`.
- `record_decision` only when `state = in_progress`, the `run_id` matches the run holding the claim, and no decision exists.
- `pay`: decision is approve, `amount = payout`, no payment exists, and (`payout ≤ limit` or a sign-off exists); a successful pay moves the claim to `decided`.
- `sign_off`: `state = waiting_for_sign_off`, handler exists with `can_approve_over_limit`, no sign-off exists; records the sign-off and pays in one transaction.
- `fail`: `state = in_progress` and no payment → delete the decision, add an `error` step, `state = waiting`.
- The approval limit is read from `company.payout_approval_limit`.
