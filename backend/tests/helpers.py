APPROVE = {
    "run_id": "run-1",
    "outcome": "approve",
    "payout": "420.00",
    "calculation": "245.00 + 95.00 + 80.00 = 420.00",
    "explanation": "The flight was canceled. The costs are covered. We pay them.",
    "sections": [3],
}


def start(client, claim_id="CLM-1001", run_id="run-1"):
    return client.post(f"/api/claims/{claim_id}/start", json={"run_id": run_id})


def decide(client, claim_id="CLM-1001", **changes):
    return client.post(f"/api/claims/{claim_id}/decision", json=APPROVE | changes)


def pay(client, amount, claim_id="CLM-1001"):
    return client.post(f"/api/claims/{claim_id}/payment", json={"amount": amount})
