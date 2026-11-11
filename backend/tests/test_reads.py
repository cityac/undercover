from backend.main import app


def test_queue(client):
    rows = client.get("/api/claims").json()
    assert len(rows) == 25
    assert [r["claim_id"] for r in rows][:2] == ["CLM-1001", "CLM-1002"]
    first = rows[0]
    assert first["customer_name"] == "Maya Patel"
    assert first["amount_claimed"] == "420.00"
    assert first["state"] == "waiting"
    assert first["outcome"] is None


def test_claim_in_full(client):
    claim = client.get("/api/claims/CLM-1001").json()
    assert claim["policy_id"] == "POL-2001"
    assert [i["amount"] for i in claim["items"]] == ["245.00", "95.00", "80.00"]
    assert claim["documents"][0]["name"] == "Meridian Air cancellation notice"
    assert claim["decision"] is None
    assert claim["sign_off"] is None
    assert claim["payment"] is None


def test_policy(client):
    policy = client.get("/api/policies/POL-2001").json()
    assert policy["plan"]["plan"] == "premium"
    assert policy["plan"]["trip_delay_max"] == "800.00"
    assert policy["plan"]["trip_delay_waiting_hours"] == 6
    assert policy["trip_cost"] == "3100.00"
    assert policy["travelers"] == ["Maya Patel"]


def test_customer_has_no_contact_details(client):
    customer = client.get("/api/customers/CUS-3001").json()
    assert customer["name"] == "Maya Patel"
    assert customer["previous_claims"][0]["amount_paid"] == "140.00"
    for private in ["email", "phone", "address", "date_of_birth"]:
        assert private not in customer


def test_policy_wording(client):
    wording = client.get("/api/policy-wording").json()
    assert wording["text"].startswith("# UnderCover Travel Insurance")
    assert wording["sections"][2] == {"number": 3, "title": "Trip Delay"}
    assert len(wording["sections"]) == 12


def test_handlers(client):
    handlers = client.get("/api/handlers").json()
    assert [h["handler_id"] for h in handlers] == ["HND-01", "HND-02", "HND-03"]
    assert "email" not in handlers[0]


def test_steps_empty(client):
    assert client.get("/api/claims/CLM-1001/steps").json() == []


def test_not_found(client):
    for path in [
        "/api/claims/CLM-0000",
        "/api/claims/CLM-0000/steps",
        "/api/policies/POL-0000",
        "/api/customers/CUS-0000",
    ]:
        response = client.get(path)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


def test_instructions(client):
    text = client.get("/api/instructions").json()["text"]
    assert text.startswith("# UnderCover Agent instructions")
    assert "evals" not in text
    assert "answer key" not in text


def test_no_route_changes_instructions_or_resets():
    for route in app.routes:
        path = getattr(route, "path", "")
        methods = getattr(route, "methods", set())
        if path == "/api/instructions":
            assert methods == {"GET"}
        for word in ["reset", "release", "seed"]:
            assert word not in path
