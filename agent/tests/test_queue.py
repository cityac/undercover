from langchain_core.messages import AIMessage

from agent import __main__ as cli
from agent import main
from agent.tests.conftest import calls, stub

DECLINE = {
    "outcome": "decline",
    "payout": "0.00",
    "calculation": "Nothing is paid.",
    "explanation": "The wording excludes this loss. Nothing is paid.",
    "sections": [9],
}


def test_work_queue_carries_on_past_failures():
    results = {"CLM-1": "decided", "CLM-2": "waiting", "CLM-3": "waiting_for_sign_off"}
    summary = cli.work_queue(list(results), lambda claim_id, _: results[claim_id])
    assert summary.splitlines() == [
        "decided: 1 (CLM-1)",
        "failed: 1 (CLM-2)",
        "waiting_for_sign_off: 1 (CLM-3)",
    ]


def test_whole_queue_with_a_scripted_model(backend, monkeypatch):
    def scripted(claim_id, thread_id):
        decision = DECLINE | {"claim_id": claim_id}
        model = stub(calls(("record_decision", decision)), AIMessage(content="Done."))
        return main.run(claim_id, thread_id, model)

    monkeypatch.setattr(cli, "run", scripted)
    summary = cli.main([])
    assert summary.startswith("decided: 25")
    states = {row["state"] for row in backend.get("/api/claims").json()}
    assert states == {"decided"}
    assert cli.main([]) == "No claims are waiting."


def test_one_claim(monkeypatch):
    monkeypatch.setattr(cli, "run", lambda claim_id, thread_id: "decided")
    assert cli.main(["CLM-1001"]) == "decided: 1 (CLM-1001)"
    assert cli.run_id("CLM-1001").startswith("run-CLM-1001-")
