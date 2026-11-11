from backend.release import main
from backend.tests.helpers import decide, pay, start


def test_release_a_stuck_claim(client):
    start(client)
    decide(client)
    assert main(["CLM-1001"]) == "CLM-1001 is waiting again"
    claim = client.get("/api/claims/CLM-1001").json()
    assert claim["decision"] is None
    steps = client.get("/api/claims/CLM-1001/steps").json()
    assert steps[-1]["kind"] == "error"


def test_release_refusals(client):
    assert main([]).startswith("Usage")
    assert main(["CLM-0000"]) == "Not released: CLM-0000 not found"
    assert main(["CLM-1001"]) == "Not released: the claim is not in progress"
    start(client)
    decide(client)
    pay(client, "420.00")
    assert main(["CLM-1001"]) == "Not released: the claim is not in progress"
