import inspect

from backend import seed as seed_module
from backend.db import connect, create_schema, is_empty
from backend.seed import SOURCES, reset, seed

COUNTS = {
    "claims": "SELECT COUNT(*) FROM claims",
    "policies": "SELECT COUNT(*) FROM policies",
    "customers": "SELECT COUNT(*) FROM customers",
    "plans": "SELECT COUNT(*) FROM plans",
    "handlers": "SELECT COUNT(*) FROM handlers",
    "policy_sections": "SELECT COUNT(*) FROM policy_sections",
    "steps": "SELECT COUNT(*) FROM steps",
}


def count(conn, table):
    return conn.execute(COUNTS[table]).fetchone()[0]


def test_seed_loads_every_record():
    conn = connect()
    create_schema(conn)
    assert is_empty(conn)
    seed(conn)
    assert not is_empty(conn)
    assert count(conn, "claims") == 25
    assert count(conn, "policies") == 50
    assert count(conn, "customers") == 49
    assert count(conn, "plans") == 3
    assert count(conn, "handlers") == 3
    assert count(conn, "policy_sections") == 12
    states = {row[0] for row in conn.execute("SELECT state FROM claims")}
    assert states == {"waiting"}
    first = conn.execute("SELECT * FROM claims ORDER BY seq LIMIT 1").fetchone()
    assert first["claim_id"] == "CLM-1001"
    assert first["amount_claimed_cents"] == 42000


def test_seed_reads_only_the_allowed_files():
    source = inspect.getsource(seed_module)
    for hidden in ["evals", "security", "claims_manual", "knowledge"]:
        assert hidden not in source
    assert all(not name.startswith("evals") for name in SOURCES)


def test_reset_drops_work():
    reset()
    conn = connect()
    conn.execute(
        "INSERT INTO steps (claim_id, run_id, kind, content, created_at)"
        " VALUES ('CLM-1001', 'r', 'read', 'x', 'now')"
    )
    conn.commit()
    assert reset() == 25
    assert count(connect(), "steps") == 0
