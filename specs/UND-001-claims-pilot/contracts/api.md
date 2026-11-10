# API Contract — UND-001 Claims Pilot

Base `/api`. JSON. Every operation has an `operation_id` (below), a one-line docstring and no optional inputs. Amounts are decimal strings with two places (`"1250.00"`). Errors: `404 {"detail": "..."}` for an unknown id; `409 {"detail": "<failed check>"}` for a refused move; `422` for invalid input.

## Reads

| Method | Path | operation_id | Response |
|---|---|---|---|
| GET | `/health` | `health` | `{"status": "ok"}` |
| GET | `/claims` | `list_claims` | `[QueueRow]` in claim id order |
| GET | `/claims/{claim_id}` | `get_claim` | `Claim` |
| GET | `/claims/{claim_id}/steps` | `list_steps` | `[Step]` in order |
| GET | `/policies/{policy_id}` | `get_policy` | `Policy` (with `plan` details) |
| GET | `/customers/{customer_id}` | `get_customer` | `Customer` (no contact details) |
| GET | `/policy-wording` | `get_policy_wording` | `{"text": str, "sections": [{"number": int, "title": str}]}` |
| GET | `/instructions` | `get_instructions` | `{"text": str}` |
| GET | `/handlers` | `list_handlers` | `[{"handler_id", "name", "role", "can_approve_over_limit"}]` |

`QueueRow`: `claim_id, customer_name, claim_type, submitted_on, amount_claimed, state, outcome|null`.

`Claim`: `claim_id, policy_id, customer_id, customer_name, claim_type, submitted_on, incident_date, incident_location, summary, story, items[{description, category, amount}], amount_claimed, documents[{name, type, content}], state, decision|null, sign_off|null, payment|null`.
- `decision`: `outcome, payout, calculation, explanation, sections[{number, title}], decided_at`.
- `sign_off`: `handler_id, handler_name, signed_at`. `payment`: `amount, paid_at`.

`Step`: `id, run_id, kind, content, created_at`.

## Writes

| Method | Path | operation_id | Body | Success | Refusals (409) |
|---|---|---|---|---|---|
| POST | `/claims/{claim_id}/start` | `start_claim` | `{"run_id": str}` | `Claim` (`in_progress`) | not waiting |
| POST | `/claims/{claim_id}/decision` | `record_decision` | `{"run_id", "outcome", "payout", "calculation", "explanation", "sections": [int]}` | `Claim` | not in progress; wrong run; already decided; payout rules; unknown section |
| POST | `/claims/{claim_id}/payment` | `pay_claim` | `{"amount": str}` | `Claim` (`decided`) | not approved; amount ≠ payout; already paid; sign-off required |
| POST | `/claims/{claim_id}/sign-off` | `sign_off_claim` | `{"handler_id": str}` | `Claim` (`decided`, with payment) | not waiting for sign-off; unknown handler; handler not allowed; already signed off |
| POST | `/claims/{claim_id}/fail` | `fail_claim` | `{"run_id": str, "error": str}` | `Claim` (`waiting`) | not in progress; wrong run; already paid |
| POST | `/claims/{claim_id}/steps` | `add_step` | `{"run_id", "kind", "content"}` | `Step` | — (422 on unknown kind) |

There is no route for reset, release or editing instructions.

## Command line

| Command | Effect |
|---|---|
| `uv run -m backend.seed` | Reset: drop all work, reseed from `data/` |
| `uv run -m backend.release CLM-1001` | Release an `in_progress` claim with no payment back to `waiting`, with an error step |
| `uv run -m agent` | Work every waiting claim in order; print a summary |
| `uv run -m agent CLM-1001` | Work one claim |

## Agent tools (LLM-callable)

`get_claim(claim_id)`, `get_policy(policy_id)`, `get_customer(customer_id)`, `get_policy_wording()`, `record_decision(claim_id, outcome, payout, calculation, explanation, sections)`, `pay_claim(claim_id, amount)`. Tool results return the API's JSON, or the refusal text for a 409/422 so the model can correct itself.
