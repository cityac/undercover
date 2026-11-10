from fastapi.testclient import TestClient

from backend.db import connect, db_path
from backend.main import app


def test_db_path_default(monkeypatch):
    monkeypatch.delenv("UNDERCOVER_DB")
    assert str(db_path()) == "undercover.db"


def test_restart_keeps_work():
    with TestClient(app):
        pass
    conn = connect()
    conn.execute(
        "INSERT INTO steps (claim_id, run_id, kind, content, created_at)"
        " VALUES ('CLM-1001', 'r', 'read', 'kept', 'now')"
    )
    conn.commit()
    with TestClient(app):
        pass
    assert connect().execute("SELECT content FROM steps").fetchone()[0] == "kept"
