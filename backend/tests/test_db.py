from concurrent.futures import ThreadPoolExecutor

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


def test_connection_works_across_threads():
    conn = connect()
    with ThreadPoolExecutor(1) as pool:
        assert pool.submit(lambda: conn.execute("SELECT 1").fetchone()[0]).result() == 1
