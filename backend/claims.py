"""Claims: reading the records and every rule for moving a claim on."""

import json
import sqlite3
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from backend import models
from backend.money import to_cents, to_str

INSTRUCTIONS = Path(__file__).resolve().parent / "instructions.md"
BENEFIT_CAPS = {
    "trip_cancellation": "trip_cancellation_max_cents",
    "trip_interruption": "trip_cancellation_max_cents",
    "trip_delay": "trip_delay_max_cents",
    "baggage_delay": "baggage_delay_max_cents",
    "baggage": "baggage_max_cents",
    "passport": "passport_max_cents",
    "emergency_medical": "emergency_medical_max_cents",
}


class NotFoundError(Exception):
    """A record that does not exist."""


class RefusedError(Exception):
    """A move the rules do not allow; the message names the failed check."""


def now() -> str:
    """Return the current time in ISO format."""
    return datetime.now(UTC).isoformat(timespec="seconds")


def row(conn: sqlite3.Connection, sql: str, *args: object) -> sqlite3.Row:
    """Return one row, or raise NotFoundError."""
    found = conn.execute(sql, args).fetchone()
    if found is None:
        raise NotFoundError(f"{args[0]} not found")
    return found


def approval_limit(conn: sqlite3.Connection) -> int:
    """Return the payout approval limit in cents."""
    value = row(
        conn, "SELECT value FROM company WHERE key = ?", "payout_approval_limit"
    )
    return to_cents(json.loads(value[0]))


def sections_by_number(conn: sqlite3.Connection) -> dict[int, str]:
    """Return the policy wording's section titles by number."""
    return dict(conn.execute("SELECT number, title FROM policy_sections").fetchall())


# Reads


def list_queue(conn: sqlite3.Connection) -> list[models.QueueRow]:
    """Return the queue in claim order."""
    rows = conn.execute(
        "SELECT c.claim_id, u.name, c.claim_type, c.submitted_on,"
        " c.amount_claimed_cents, c.state, d.outcome FROM claims c"
        " JOIN customers u USING (customer_id)"
        " LEFT JOIN decisions d USING (claim_id) ORDER BY c.seq"
    ).fetchall()
    return [
        models.QueueRow(
            claim_id=r[0],
            customer_name=r[1],
            claim_type=r[2],
            submitted_on=r[3],
            amount_claimed=to_str(r[4]),
            state=r[5],
            outcome=r[6],
        )
        for r in rows
    ]


def get_decision(conn: sqlite3.Connection, claim_id: str) -> models.Decision | None:
    """Return the claim's decision, if it has one."""
    d = conn.execute(
        "SELECT * FROM decisions WHERE claim_id = ?", (claim_id,)
    ).fetchone()
    if d is None:
        return None
    titles = sections_by_number(conn)
    return models.Decision(
        outcome=d["outcome"],
        payout=to_str(d["payout_cents"]),
        calculation=d["calculation"],
        explanation=d["explanation"],
        sections=[
            models.Section(number=n, title=titles[n]) for n in json.loads(d["sections"])
        ],
        decided_at=d["decided_at"],
    )


def get_sign_off(conn: sqlite3.Connection, claim_id: str) -> models.SignOff | None:
    """Return the claim's sign-off, if it has one."""
    s = conn.execute(
        "SELECT s.handler_id, h.name, s.signed_at FROM sign_offs s"
        " JOIN handlers h USING (handler_id) WHERE s.claim_id = ?",
        (claim_id,),
    ).fetchone()
    if s is None:
        return None
    return models.SignOff(handler_id=s[0], handler_name=s[1], signed_at=s[2])


def get_payment(conn: sqlite3.Connection, claim_id: str) -> models.Payment | None:
    """Return the claim's payment, if it has one."""
    p = conn.execute(
        "SELECT * FROM payments WHERE claim_id = ?", (claim_id,)
    ).fetchone()
    if p is None:
        return None
    return models.Payment(amount=to_str(p["amount_cents"]), paid_at=p["paid_at"])


def get_claim(conn: sqlite3.Connection, claim_id: str) -> models.Claim:
    """Return one claim in full, with its decision, sign-off and payment."""
    c = row(
        conn,
        "SELECT c.*, u.name AS customer_name FROM claims c"
        " JOIN customers u USING (customer_id) WHERE c.claim_id = ?",
        claim_id,
    )
    items = [
        models.Item(
            description=i["description"],
            category=i["category"],
            amount=to_str(i["amount_cents"]),
        )
        for i in json.loads(c["items"])
    ]
    return models.Claim(
        claim_id=c["claim_id"],
        policy_id=c["policy_id"],
        customer_id=c["customer_id"],
        customer_name=c["customer_name"],
        claim_type=c["claim_type"],
        submitted_on=c["submitted_on"],
        incident_date=c["incident_date"],
        incident_location=c["incident_location"],
        summary=c["summary"],
        story=c["story"],
        items=items,
        amount_claimed=to_str(c["amount_claimed_cents"]),
        documents=[models.Document(**d) for d in json.loads(c["documents"])],
        state=c["state"],
        decision=get_decision(conn, claim_id),
        sign_off=get_sign_off(conn, claim_id),
        payment=get_payment(conn, claim_id),
    )


def get_policy(conn: sqlite3.Connection, policy_id: str) -> models.Policy:
    """Return one policy with its plan."""
    p = row(conn, "SELECT * FROM policies WHERE policy_id = ?", policy_id)
    plan = row(conn, "SELECT * FROM plans WHERE plan = ?", p["plan"])
    plan_fields = {
        key.removesuffix("_cents"): to_str(value) if key.endswith("_cents") else value
        for key, value in dict(plan).items()
    }
    return models.Policy(
        policy_id=p["policy_id"],
        customer_id=p["customer_id"],
        plan=models.Plan.model_validate(plan_fields),
        add_ons=json.loads(p["add_ons"]),
        purchased_on=p["purchased_on"],
        sold_through=p["sold_through"],
        destination=p["destination"],
        departs_on=p["departs_on"],
        returns_on=p["returns_on"],
        trip_cost=to_str(p["trip_cost_cents"]),
        travelers=json.loads(p["travelers"]),
        status=p["status"],
    )


def get_customer(conn: sqlite3.Connection, customer_id: str) -> models.Customer:
    """Return a customer's name and claim history, without contact details."""
    c = row(conn, "SELECT * FROM customers WHERE customer_id = ?", customer_id)
    previous = [
        models.PreviousClaim(
            claim_id=p["claim_id"],
            filed_on=p["filed_on"],
            incident_date=p["incident_date"],
            claim_type=p["claim_type"],
            summary=p["summary"],
            outcome=p["outcome"],
            amount_paid=to_str(to_cents(p["amount_paid"])),
        )
        for p in json.loads(c["previous_claims"])
    ]
    return models.Customer(
        customer_id=c["customer_id"],
        name=c["name"],
        customer_since=c["customer_since"],
        previous_claims=previous,
    )


def get_policy_wording(conn: sqlite3.Connection) -> models.PolicyWording:
    """Return the policy wording and its sections."""
    text = row(conn, "SELECT content FROM documents WHERE name = ?", "policy_wording")[
        0
    ]
    sections = [
        models.Section(number=n, title=t) for n, t in sections_by_number(conn).items()
    ]
    return models.PolicyWording(text=text, sections=sections)


def get_instructions() -> models.Instructions:
    """Return the agent's instructions."""
    return models.Instructions(text=INSTRUCTIONS.read_text(encoding="utf-8"))


def list_handlers(conn: sqlite3.Connection) -> list[models.Handler]:
    """Return the claims handlers."""
    return [
        models.Handler(
            handler_id=h[0], name=h[1], role=h[2], can_approve_over_limit=bool(h[3])
        )
        for h in conn.execute("SELECT * FROM handlers ORDER BY handler_id")
    ]


def list_steps(conn: sqlite3.Connection, claim_id: str) -> list[models.Step]:
    """Return a claim's steps in the order they happened."""
    row(conn, "SELECT claim_id FROM claims WHERE claim_id = ?", claim_id)
    return [
        models.Step(
            id=s["id"],
            run_id=s["run_id"],
            kind=s["kind"],
            content=s["content"],
            created_at=s["created_at"],
        )
        for s in conn.execute(
            "SELECT * FROM steps WHERE claim_id = ? ORDER BY id", (claim_id,)
        )
    ]


# Moves


def state_of(conn: sqlite3.Connection, claim_id: str) -> str:
    """Return a claim's state."""
    return row(conn, "SELECT state FROM claims WHERE claim_id = ?", claim_id)[0]


def set_state(conn: sqlite3.Connection, claim_id: str, state: str) -> None:
    """Move a claim to a new state."""
    conn.execute("UPDATE claims SET state = ? WHERE claim_id = ?", (state, claim_id))


def require_run(conn: sqlite3.Connection, claim_id: str, run_id: str) -> None:
    """Refuse unless the claim is in progress under this run."""
    if state_of(conn, claim_id) != "in_progress":
        raise RefusedError("the claim is not in progress")
    latest = conn.execute(
        "SELECT run_id FROM runs WHERE claim_id = ? ORDER BY rowid DESC LIMIT 1",
        (claim_id,),
    ).fetchone()
    if latest is None or latest[0] != run_id:
        raise RefusedError("another run holds this claim")


def add_step(
    conn: sqlite3.Connection, claim_id: str, request: models.StepRequest
) -> models.Step:
    """Record one of the agent's steps on a claim."""
    state_of(conn, claim_id)
    with conn:
        conn.execute(
            "INSERT INTO steps (claim_id, run_id, kind, content, created_at)"
            " VALUES (?, ?, ?, ?, ?)",
            (claim_id, request.run_id, request.kind, request.content, now()),
        )
    return list_steps(conn, claim_id)[-1]


def start(conn: sqlite3.Connection, claim_id: str, run_id: str) -> models.Claim:
    """Take a waiting claim for a run."""
    with conn:
        if state_of(conn, claim_id) != "waiting":
            raise RefusedError("the claim is not waiting")
        conn.execute("INSERT INTO runs VALUES (?, ?, ?)", (run_id, claim_id, now()))
        set_state(conn, claim_id, "in_progress")
    return get_claim(conn, claim_id)


def payout_cap(conn: sqlite3.Connection, claim_id: str) -> int:
    """Return the most an approval may pay: the amount claimed or the benefit cap."""
    c = row(
        conn,
        "SELECT c.claim_type, c.amount_claimed_cents, p.trip_cost_cents, l.*"
        " FROM claims c JOIN policies p USING (policy_id)"
        " JOIN plans l ON l.plan = p.plan WHERE c.claim_id = ?",
        claim_id,
    )
    cap = c[BENEFIT_CAPS[c["claim_type"]]]
    if c["claim_type"] in {"trip_cancellation", "trip_interruption"}:
        cap = min(cap, c["trip_cost_cents"])
    return min(cap, c["amount_claimed_cents"])


def check_decision(
    conn: sqlite3.Connection, claim_id: str, request: models.DecisionRequest
) -> int:
    """Refuse a decision that breaks a rule; return the payout in cents."""
    try:
        payout = to_cents(request.payout)
    except ValueError as error:
        raise RefusedError(str(error)) from error
    if request.outcome == "approve":
        if payout == 0:
            raise RefusedError("an approval must pay more than $0.00; decline instead")
        if payout > payout_cap(conn, claim_id):
            raise RefusedError(
                "the payout is more than the amount claimed or the plan's maximum"
            )
    elif payout != 0:
        raise RefusedError("a decline or referral pays $0.00")
    unknown = set(request.sections) - set(sections_by_number(conn))
    if unknown:
        raise RefusedError(f"no such policy section: {sorted(unknown)}")
    return payout


def record_decision(
    conn: sqlite3.Connection, claim_id: str, request: models.DecisionRequest
) -> models.Claim:
    """Record the agent's decision and move the claim on."""
    with conn:
        require_run(conn, claim_id, request.run_id)
        if conn.execute(
            "SELECT 1 FROM decisions WHERE claim_id = ?", (claim_id,)
        ).fetchone():
            raise RefusedError("the claim already has a decision")
        payout = check_decision(conn, claim_id, request)
        conn.execute(
            "INSERT INTO decisions VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                claim_id,
                request.run_id,
                request.outcome,
                payout,
                request.calculation,
                request.explanation,
                json.dumps(request.sections),
                now(),
            ),
        )
        if request.outcome != "approve":
            set_state(conn, claim_id, "decided")
        elif payout > approval_limit(conn):
            set_state(conn, claim_id, "waiting_for_sign_off")
    return get_claim(conn, claim_id)


def pay_in(conn: sqlite3.Connection, claim_id: str, amount: int) -> None:
    """Record a payment inside an open transaction, if every check passes."""
    d = conn.execute(
        "SELECT outcome, payout_cents FROM decisions WHERE claim_id = ?", (claim_id,)
    ).fetchone()
    if d is None or d[0] != "approve":
        raise RefusedError("the claim is not approved")
    if conn.execute(
        "SELECT 1 FROM payments WHERE claim_id = ?", (claim_id,)
    ).fetchone():
        raise RefusedError("the claim has already been paid")
    if amount != d[1]:
        raise RefusedError(
            f"the amount must equal the approved payout of ${to_str(d[1])}"
        )
    signed = conn.execute(
        "SELECT 1 FROM sign_offs WHERE claim_id = ?", (claim_id,)
    ).fetchone()
    if d[1] > approval_limit(conn) and not signed:
        raise RefusedError(
            "a payout over $1,000.00 needs a handler's sign-off before it is paid"
        )
    conn.execute("INSERT INTO payments VALUES (?, ?, ?)", (claim_id, amount, now()))
    set_state(conn, claim_id, "decided")


def pay(conn: sqlite3.Connection, claim_id: str, amount: Decimal) -> models.Claim:
    """Pay an approved claim through the one guarded payment path."""
    try:
        cents = to_cents(amount)
    except ValueError as error:
        raise RefusedError(str(error)) from error
    with conn:
        state_of(conn, claim_id)
        pay_in(conn, claim_id, cents)
    return get_claim(conn, claim_id)


def sign_off(conn: sqlite3.Connection, claim_id: str, handler_id: str) -> models.Claim:
    """Record a handler's sign-off and pay the approved payout, together."""
    with conn:
        if state_of(conn, claim_id) != "waiting_for_sign_off":
            raise RefusedError("the claim is not waiting for sign-off")
        handler = conn.execute(
            "SELECT can_approve_over_limit FROM handlers WHERE handler_id = ?",
            (handler_id,),
        ).fetchone()
        if handler is None:
            raise RefusedError(f"{handler_id} is not a claims handler")
        if not handler[0]:
            raise RefusedError(f"{handler_id} may not approve over the limit")
        if conn.execute(
            "SELECT 1 FROM sign_offs WHERE claim_id = ?", (claim_id,)
        ).fetchone():
            raise RefusedError("the claim has already been signed off")
        conn.execute(
            "INSERT INTO sign_offs VALUES (?, ?, ?)", (claim_id, handler_id, now())
        )
        payout = conn.execute(
            "SELECT payout_cents FROM decisions WHERE claim_id = ?", (claim_id,)
        ).fetchone()[0]
        pay_in(conn, claim_id, payout)
    return get_claim(conn, claim_id)


def back_to_waiting(
    conn: sqlite3.Connection, claim_id: str, run_id: str, error: str
) -> None:
    """Inside a transaction: drop an unpaid decision and return the claim to waiting."""
    if conn.execute(
        "SELECT 1 FROM payments WHERE claim_id = ?", (claim_id,)
    ).fetchone():
        raise RefusedError("the claim has been paid")
    conn.execute("DELETE FROM decisions WHERE claim_id = ?", (claim_id,))
    conn.execute(
        "INSERT INTO steps (claim_id, run_id, kind, content, created_at)"
        " VALUES (?, ?, 'error', ?, ?)",
        (claim_id, run_id, error, now()),
    )
    set_state(conn, claim_id, "waiting")


def fail(
    conn: sqlite3.Connection, claim_id: str, request: models.FailRequest
) -> models.Claim:
    """Undo a failed run: no decision is left and the claim waits again."""
    with conn:
        require_run(conn, claim_id, request.run_id)
        back_to_waiting(conn, claim_id, request.run_id, request.error)
    return get_claim(conn, claim_id)


def release(conn: sqlite3.Connection, claim_id: str) -> models.Claim:
    """Free a claim left in progress by a run that died."""
    with conn:
        if state_of(conn, claim_id) != "in_progress":
            raise RefusedError("the claim is not in progress")
        back_to_waiting(conn, claim_id, "release", "Released from the command line")
    return get_claim(conn, claim_id)
