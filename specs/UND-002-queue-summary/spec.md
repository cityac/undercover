# Feature Specification: Queue summary

**Feature Branch**: `feature/UND-002-queue-summary`
**Created**: 2026-11-11
**Status**: Ready
**Input**: Student request: "4 separate sections under the Claims queue header: group and show the total amount of claims grouped by type: Waiting, ..."
**Scope**: S (dashboard only, no backend change)

## User Scenarios & Testing

### User Story 1 — See the queue at a glance (Priority: P1)

A handler opens the queue and sees, above the table, four sections, one per claim state in this order: Waiting, In progress, Waiting for sign-off, Decided. Each section shows how many claims are in that state and the total amount claimed across them.

**Independent Test**: Open the queue with claims in several states; each section shows the right count and dollar total.

**Acceptance Scenarios**:

1. **Given** the starting queue (25 claims, all waiting), **When** the queue opens, **Then** Waiting shows 25 claims and the sum of all amounts claimed, and the other three show 0 claims and $0.00.
2. **Given** claims in different states, **When** the queue opens, **Then** each section's count and total match the claims in that state, and the four counts add up to the number of rows.
3. **Given** the queue page is open, **When** a claim changes state, **Then** the sections update on the next refresh, together with the table.

### Edge Cases

- A state with no claims shows "0 claims" and "$0.00"; the section is still shown.
- One claim shows "1 claim" (singular).
- Totals are summed exactly in cents, with no floating-point drift.

## Requirements

- **FR-001**: The queue page MUST show four sections directly under the "Claims queue" heading and above the table, in the order Waiting, In progress, Waiting for sign-off, Decided.
- **FR-002**: Each section MUST show the state label, styled like that state's badge, plus the number of claims and the total amount claimed in US dollars.
- **FR-003**: The totals MUST be computed from the same queue data as the table, so the two never disagree.
- **FR-004**: The totals MUST be exact to the cent.
- **FR-005**: The sections MUST follow `docs/BRAND.md` tokens, in light and dark themes, and wrap on narrow screens.

## Success Criteria

- **SC-001**: For any queue, the four counts sum to the number of table rows, and each total equals the sum of that state's amounts claimed.

## Assumptions

- "Type" in the request means the claim state; the four states are those of UND-001.
- "Total amount" means the amount claimed. Payouts are not totalled.
- No new API: the summary is derived from `GET /api/claims`.
