from langchain_core.messages import AIMessage

from agent import main
from agent.tests.conftest import calls, stub

DECISION = {
    "claim_id": "CLM-1001",
    "outcome": "approve",
    "payout": "420.00",
    "calculation": "245.00 + 95.00 + 80.00 = 420.00",
    "explanation": "The flight was canceled for a crew problem. The costs are covered.",
    "sections": [3],
}


def kinds(backend, claim_id="CLM-1001"):
    return [s["kind"] for s in backend.get(f"/api/claims/{claim_id}/steps").json()]


def test_tools_are_the_allow_list():
    names = [t.name for t in main.tools("run-1")]
    assert names == [
        "get_claim",
        "get_policy",
        "get_customer",
        "get_policy_wording",
        "record_decision",
        "pay_claim",
    ]
    for forbidden in ["sign", "release", "reset", "start", "fail"]:
        assert all(forbidden not in name for name in names)


def test_read_tools(backend):
    assert "Maya Patel" in main.get_claim.invoke({"claim_id": "CLM-1001"})
    assert "premium" in main.get_policy.invoke({"policy_id": "POL-2001"})
    customer = main.get_customer.invoke({"customer_id": "CUS-3001"})
    assert "CLM-0412" in customer
    assert "email" not in customer
    assert main.get_policy_wording.invoke({}).startswith("# UnderCover")


def test_approve_within_limit_is_paid(backend):
    model = stub(
        calls(("get_claim", {"claim_id": "CLM-1001"}), text="I will read the claim."),
        calls(("record_decision", DECISION)),
        calls(("pay_claim", {"claim_id": "CLM-1001", "amount": "420.00"})),
        AIMessage(content="Approved and paid."),
    )
    assert main.run("CLM-1001", "run-1", model) == "decided"
    claim = backend.get("/api/claims/CLM-1001").json()
    assert claim["payment"]["amount"] == "420.00"
    assert kinds(backend) == [
        "reasoning",
        "read",
        "read",
        "decision",
        "decision",
        "payment",
        "payment",
        "reasoning",
    ]


def test_decline(backend):
    decline = DECISION | {"outcome": "decline", "payout": "0.00"}
    model = stub(calls(("record_decision", decline)), AIMessage(content="Declined."))
    assert main.run("CLM-1001", "run-1", model) == "decided"
    assert (
        backend.get("/api/claims/CLM-1001").json()["decision"]["outcome"] == "decline"
    )


def test_over_limit_payment_is_refused_and_waits(backend):
    big = DECISION | {"claim_id": "CLM-1003", "payout": "1500.00", "sections": [7]}
    model = stub(
        calls(("record_decision", big)),
        calls(("pay_claim", {"claim_id": "CLM-1003", "amount": "1500.00"})),
        AIMessage(content="Waiting for sign-off."),
    )
    assert main.run("CLM-1003", "run-1", model) == "waiting_for_sign_off"
    claim = backend.get("/api/claims/CLM-1003").json()
    assert claim["payment"] is None
    steps = backend.get("/api/claims/CLM-1003/steps").json()
    refusal = [s for s in steps if s["kind"] == "payment" and "Refused" in s["content"]]
    assert "sign-off" in refusal[0]["content"]


def test_refused_decision_is_shown_to_the_model(backend):
    wrong = DECISION | {"payout": "999.00"}
    model = stub(
        calls(("record_decision", wrong)),
        calls(("record_decision", DECISION | {"outcome": "refer", "payout": "0.00"})),
        AIMessage(content="Referred."),
    )
    assert main.run("CLM-1001", "run-1", model) == "decided"
    steps = backend.get("/api/claims/CLM-1001/steps").json()
    assert "Refused" in steps[1]["content"]


def test_a_failure_returns_the_claim(backend, monkeypatch):
    def broken(*args):
        raise RuntimeError("model unavailable")

    monkeypatch.setattr(main, "work", broken)
    assert main.run("CLM-1001", "run-1", stub()) == "waiting"
    claim = backend.get("/api/claims/CLM-1001").json()
    assert claim["state"] == "waiting"
    assert kinds(backend) == ["error"]


def test_a_run_that_never_pays_returns_the_claim(backend):
    model = stub(calls(("record_decision", DECISION)), AIMessage(content="Done."))
    assert main.run("CLM-1001", "run-1", model) == "waiting"
    claim = backend.get("/api/claims/CLM-1001").json()
    assert claim["decision"] is None
    assert kinds(backend)[-1] == "error"


def test_a_claim_that_is_not_waiting(backend):
    backend.post("/api/claims/CLM-1001/start", json={"run_id": "other"})
    assert main.run("CLM-1001", "run-1", stub()).startswith("Refused")


def test_model_name(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.delenv("MODEL_NAME", raising=False)
    assert main.model().model_name == "openai/gpt-6-luna"
    monkeypatch.setenv("MODEL_NAME", "openrouter/free")
    assert main.model().model_name == "openrouter/free"
