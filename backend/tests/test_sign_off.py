from backend.db import connect
from backend.tests.helpers import decide, pay, start

BIG = "CLM-1003"


def approve_big(client, payout="1500.00"):
    start(client, claim_id=BIG)
    return decide(client, claim_id=BIG, payout=payout, sections=[7]).json()


def sign_off(client, handler_id="HND-01", claim_id=BIG):
    return client.post(
        f"/api/claims/{claim_id}/sign-off", json={"handler_id": handler_id}
    )


def test_over_limit_waits_and_payment_is_blocked(client):
    claim = approve_big(client, "1000.01")
    assert claim["state"] == "waiting_for_sign_off"
    assert claim["payment"] is None
    refused = pay(client, "1000.01", claim_id=BIG)
    assert refused.status_code == 409
    assert "sign-off" in refused.json()["detail"]
    after = client.get(f"/api/claims/{BIG}").json()
    assert after["state"] == "waiting_for_sign_off"
    assert after["payment"] is None


def test_exactly_the_limit_needs_no_sign_off(client):
    approve_big(client, "1000.00")
    assert pay(client, "1000.00", claim_id=BIG).json()["state"] == "decided"


def test_sign_off_pays(client):
    approve_big(client)
    claim = sign_off(client).json()
    assert claim["state"] == "decided"
    assert claim["payment"]["amount"] == "1500.00"
    assert claim["sign_off"]["handler_name"] == "Dana Whitfield"
    assert sign_off(client).json()["detail"] == "the claim is not waiting for sign-off"
    assert "already been paid" in pay(client, "1500.00", claim_id=BIG).json()["detail"]


def test_sign_off_refusals(client):
    assert "not waiting for sign-off" in sign_off(client).json()["detail"]
    approve_big(client)
    assert "not a claims handler" in sign_off(client, "HND-99").json()["detail"]
    conn = connect()
    conn.execute(
        "UPDATE handlers SET can_approve_over_limit = 0 WHERE handler_id = 'HND-02'"
    )
    conn.commit()
    assert "may not approve" in sign_off(client, "HND-02").json()["detail"]
    assert client.get(f"/api/claims/{BIG}").json()["sign_off"] is None


def test_already_signed_off(client):
    approve_big(client)
    conn = connect()
    conn.execute("INSERT INTO sign_offs VALUES (?, 'HND-01', 'earlier')", (BIG,))
    conn.commit()
    assert "already been signed off" in sign_off(client).json()["detail"]
