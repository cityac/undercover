"""The SQLite store."""

import os
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS company (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS plans (
    plan TEXT PRIMARY KEY, name TEXT NOT NULL,
    trip_cancellation_max_cents INTEGER NOT NULL,
    trip_delay_waiting_hours INTEGER NOT NULL, trip_delay_max_cents INTEGER NOT NULL,
    baggage_delay_waiting_hours INTEGER NOT NULL,
    baggage_delay_max_cents INTEGER NOT NULL,
    baggage_max_cents INTEGER NOT NULL, per_item_limit_cents INTEGER NOT NULL,
    passport_max_cents INTEGER NOT NULL, emergency_medical_max_cents INTEGER NOT NULL,
    deductible_cents INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS handlers (
    handler_id TEXT PRIMARY KEY, name TEXT NOT NULL, role TEXT NOT NULL,
    can_approve_over_limit INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY, name TEXT NOT NULL, email TEXT, phone TEXT,
    date_of_birth TEXT, address TEXT, customer_since TEXT NOT NULL,
    previous_claims TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS policies (
    policy_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL REFERENCES customers,
    plan TEXT NOT NULL REFERENCES plans, add_ons TEXT NOT NULL,
    purchased_on TEXT NOT NULL, sold_through TEXT NOT NULL,
    destination TEXT NOT NULL, departs_on TEXT NOT NULL, returns_on TEXT NOT NULL,
    trip_cost_cents INTEGER NOT NULL, travelers TEXT NOT NULL, status TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS policy_sections (
    number INTEGER PRIMARY KEY, title TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS documents (name TEXT PRIMARY KEY, content TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS claims (
    claim_id TEXT PRIMARY KEY, seq INTEGER NOT NULL,
    policy_id TEXT NOT NULL REFERENCES policies,
    customer_id TEXT NOT NULL REFERENCES customers,
    claim_type TEXT NOT NULL, submitted_on TEXT NOT NULL, incident_date TEXT NOT NULL,
    incident_location TEXT NOT NULL, summary TEXT NOT NULL, story TEXT NOT NULL,
    items TEXT NOT NULL, amount_claimed_cents INTEGER NOT NULL, documents TEXT NOT NULL,
    state TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY, claim_id TEXT NOT NULL REFERENCES claims,
    started_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS decisions (
    claim_id TEXT PRIMARY KEY REFERENCES claims, run_id TEXT NOT NULL,
    outcome TEXT NOT NULL, payout_cents INTEGER NOT NULL, calculation TEXT NOT NULL,
    explanation TEXT NOT NULL, sections TEXT NOT NULL, decided_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT, claim_id TEXT NOT NULL REFERENCES claims,
    run_id TEXT NOT NULL, kind TEXT NOT NULL, content TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sign_offs (
    claim_id TEXT PRIMARY KEY REFERENCES claims,
    handler_id TEXT NOT NULL REFERENCES handlers, signed_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS payments (
    claim_id TEXT PRIMARY KEY REFERENCES claims, amount_cents INTEGER NOT NULL,
    paid_at TEXT NOT NULL
);
"""

DROP_ALL = """
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS sign_offs;
DROP TABLE IF EXISTS steps;
DROP TABLE IF EXISTS decisions;
DROP TABLE IF EXISTS runs;
DROP TABLE IF EXISTS claims;
DROP TABLE IF EXISTS documents;
DROP TABLE IF EXISTS policy_sections;
DROP TABLE IF EXISTS policies;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS handlers;
DROP TABLE IF EXISTS plans;
DROP TABLE IF EXISTS company;
"""


def db_path() -> Path:
    """Return the database file named in UNDERCOVER_DB, or undercover.db."""
    return Path(os.getenv("UNDERCOVER_DB", "undercover.db"))


def connect() -> sqlite3.Connection:
    """Open the database with named rows and foreign keys on."""
    conn = sqlite3.connect(db_path(), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_schema(conn: sqlite3.Connection) -> None:
    """Create every table that does not exist yet."""
    conn.executescript(SCHEMA)


def drop_all(conn: sqlite3.Connection) -> None:
    """Drop every table."""
    conn.executescript(DROP_ALL)


def is_empty(conn: sqlite3.Connection) -> bool:
    """Return whether no claims have been loaded."""
    return conn.execute("SELECT COUNT(*) FROM claims").fetchone()[0] == 0
