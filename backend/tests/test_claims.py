import pytest

from backend.tests.helpers import decide, pay, start


def detail(response):
    return response.json()["detail"]


def test_start_takes_a_waiting_claim(client):
    assert start(client).json()["state"] == "in_progress"
    again = start(client, run_id="run-2")
    assert again.status_code == 409
    assert detail(again) == "the claim is not waiting"


def test_start_unknown_claim(client):
    assert start(client, claim_id="CLM-0000").status_code == 404


def test_approve_within_limit_then_pay(client):
    start(client)
    claim = decide(client).json()
    assert claim["state"] == "in_progress"
    assert claim["decision"]["payout"] == "420.00"
    assert claim["decision"]["sections"] == [{"number": 3, "title": "Trip Delay"}]
    paid = pay(client, "420.00").json()
    assert paid["state"] == "decided"
    assert paid["payment"]["amount"] == "420.00"
    rows = client.get("/api/claims").json()
    assert rows[0]["outcome"] == "approve"


@pytest.mark.parametrize("outcome", ["decline", "refer"])
def test_decline_or_refer_is_decided(client, outcome):
    start(client)
    claim = decide(client, outcome=outcome, payout="0.00").json()
    assert claim["state"] == "decided"
    assert claim["payment"] is None
    refused = pay(client, "0.00")
    assert detail(refused) == "the claim is not approved"


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"payout": "0.00"}, "decline instead"),
        ({"payout": "420.01"}, "more than the amount claimed"),
        ({"payout": "1.005"}, "two decimal places"),
        ({"payout": "-5.00"}, "not a valid amount"),
        ({"outcome": "decline", "payout": "10.00"}, "pays $0.00"),
        ({"sections": [3, 99]}, "no such policy section"),
        ({"run_id": "run-other"}, "another run"),
    ],
)
def test_decision_refusals(client, changes, reason):
    start(client)
    response = decide(client, **changes)
    assert response.status_code == 409
    assert reason in detail(response)
    assert client.get("/api/claims/CLM-1001").json()["decision"] is None


def test_payout_capped_by_plan_maximum(client):
    start(client, claim_id="CLM-1007")
    response = decide(client, claim_id="CLM-1007", payout="751.00", sections=[5])
    assert "plan's maximum" in detail(response)


@pytest.mark.parametrize(
    ("changes", "status"),
    [
        ({"outcome": "maybe"}, 422),
        ({"explanation": ""}, 422),
        ({"explanation": "x" * 601}, 422),
        ({"sections": []}, 422),
    ],
)
def test_decision_invalid_input(client, changes, status):
    start(client)
    assert decide(client, **changes).status_code == status


def test_decision_only_once_and_only_in_progress(client):
    assert detail(decide(client)) == "the claim is not in progress"
    start(client)
    decide(client, outcome="refer", payout="0.00")
    assert detail(decide(client)) == "the claim is not in progress"


def test_payment_checks(client):
    start(client)
    decide(client)
    assert "approved payout of $420.00" in detail(pay(client, "400.00"))
    assert "two decimal places" in detail(pay(client, "1.001"))
    pay(client, "420.00")
    assert detail(pay(client, "420.00")) == "the claim has already been paid"


def fail(client, run_id="run-1", claim_id="CLM-1001"):
    return client.post(
        f"/api/claims/{claim_id}/fail", json={"run_id": run_id, "error": "boom"}
    )


def test_fail_discards_unpaid_decision_and_keeps_steps(client):
    start(client)
    client.post(
        "/api/claims/CLM-1001/steps",
        json={"run_id": "run-1", "kind": "read", "content": "Read the claim"},
    )
    decide(client)
    claim = fail(client).json()
    assert claim["state"] == "waiting"
    assert claim["decision"] is None
    steps = client.get("/api/claims/CLM-1001/steps").json()
    assert [s["kind"] for s in steps] == ["read", "error"]
    assert steps[1]["content"] == "boom"
    assert start(client, run_id="run-2").status_code == 200


def test_fail_refusals(client):
    assert detail(fail(client)) == "the claim is not in progress"
    start(client)
    assert detail(fail(client, run_id="run-x")) == "another run holds this claim"


def test_step_kinds(client):
    response = client.post(
        "/api/claims/CLM-1001/steps",
        json={"run_id": "r", "kind": "gossip", "content": "x"},
    )
    assert response.status_code == 422
    step = client.post(
        "/api/claims/CLM-1001/steps",
        json={"run_id": "r", "kind": "reasoning", "content": "Thinking"},
    ).json()
    assert step["kind"] == "reasoning"
    assert step["id"] >= 1
