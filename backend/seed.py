"""Load UnderCover's records from data/. Run `uv run -m backend.seed` to reset."""

import json
import re
import sqlite3
from pathlib import Path
from typing import Any

from backend.db import connect, create_schema, drop_all
from backend.money import to_cents

DATA = Path(__file__).resolve().parent.parent / "data"
SOURCES = [
    "company.json",
    "plans.json",
    "handlers.json",
    "customers.json",
    "policies.json",
    "claims.json",
    "policy_wording.md",
]
PLAN_AMOUNTS = [
    "trip_cancellation_max",
    "trip_delay_max",
    "baggage_delay_max",
    "baggage_max",
    "per_item_limit",
    "passport_max",
    "emergency_medical_max",
    "deductible",
]
SECTION = re.compile(r"^## (\d+)\. (.+)$", re.MULTILINE)


def read(name: str) -> Any:
    """Read one of the source files in data/."""
    text = (DATA / name).read_text(encoding="utf-8")
    return json.loads(text) if name.endswith(".json") else text


def seed_reference(conn: sqlite3.Connection) -> None:
    """Load company settings, plans, handlers and the policy wording."""
    for key, value in read("company.json").items():
        conn.execute("INSERT INTO company VALUES (?, ?)", (key, json.dumps(value)))
    for plan in read("plans.json")["plans"]:
        amounts = [to_cents(plan[field]) for field in PLAN_AMOUNTS]
        conn.execute(
            "INSERT INTO plans (plan, name, trip_delay_waiting_hours,"
            " baggage_delay_waiting_hours, trip_cancellation_max_cents,"
            " trip_delay_max_cents, baggage_delay_max_cents, baggage_max_cents,"
            " per_item_limit_cents, passport_max_cents, emergency_medical_max_cents,"
            " deductible_cents) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                plan["plan"],
                plan["name"],
                plan["trip_delay_waiting_hours"],
                plan["baggage_delay_waiting_hours"],
                *amounts,
            ),
        )
    for handler in read("handlers.json"):
        conn.execute(
            "INSERT INTO handlers VALUES (?, ?, ?, ?)",
            (
                handler["handler_id"],
                handler["name"],
                handler["role"],
                handler["can_approve_over_limit"],
            ),
        )
    wording = read("policy_wording.md")
    conn.execute("INSERT INTO documents VALUES ('policy_wording', ?)", (wording,))
    for number, title in SECTION.findall(wording):
        conn.execute("INSERT INTO policy_sections VALUES (?, ?)", (int(number), title))


def seed_records(conn: sqlite3.Connection) -> None:
    """Load customers, policies and the claims queue."""
    for c in read("customers.json"):
        conn.execute(
            "INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                c["customer_id"],
                c["name"],
                c["email"],
                c["phone"],
                c["date_of_birth"],
                json.dumps(c["address"]),
                c["customer_since"],
                json.dumps(c["previous_claims"]),
            ),
        )
    for p in read("policies.json"):
        trip = p["trip"]
        conn.execute(
            "INSERT INTO policies VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                p["policy_id"],
                p["customer_id"],
                p["plan"],
                json.dumps(p["add_ons"]),
                p["purchased_on"],
                p["sold_through"],
                trip["destination"],
                trip["departs_on"],
                trip["returns_on"],
                to_cents(trip["trip_cost"]),
                json.dumps(p["travelers"]),
                p["status"],
            ),
        )
    for seq, claim in enumerate(read("claims.json")):
        items = [
            {**item, "amount_cents": to_cents(item.pop("amount"))}
            for item in claim["items"]
        ]
        conn.execute(
            "INSERT INTO claims VALUES"
            " (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'waiting')",
            (
                claim["claim_id"],
                seq,
                claim["policy_id"],
                claim["customer_id"],
                claim["claim_type"],
                claim["submitted_on"],
                claim["incident_date"],
                claim["incident_location"],
                claim["summary"],
                claim["story"],
                json.dumps(items),
                to_cents(claim["amount_claimed"]),
                json.dumps(claim["documents"]),
            ),
        )


def seed(conn: sqlite3.Connection) -> None:
    """Load every source file into an empty store."""
    with conn:
        seed_reference(conn)
        seed_records(conn)


def reset() -> int:
    """Drop all work and reload the starting queue; return the number of claims."""
    conn = connect()
    drop_all(conn)
    create_schema(conn)
    seed(conn)
    count = conn.execute("SELECT COUNT(*) FROM claims").fetchone()[0]
    conn.close()
    return count


if __name__ == "__main__":
    print(f"Reset: {reset()} claims waiting")
