"""Work the claims queue with `uv run -m agent`, or one claim with an id."""

import sys
from collections.abc import Callable
from datetime import UTC, datetime

from agent.main import call, run


def run_id(claim_id: str) -> str:
    """Return a new run id for a claim."""
    return f"run-{claim_id}-{datetime.now(UTC):%Y%m%d%H%M%S%f}"


def work_queue(claim_ids: list[str], runner: Callable[[str, str], str]) -> str:
    """Work each claim in order, carry on past failures, and summarize."""
    results: dict[str, list[str]] = {}
    for claim_id in claim_ids:
        state = runner(claim_id, run_id(claim_id))
        label = state if state in {"decided", "waiting_for_sign_off"} else "failed"
        results.setdefault(label, []).append(claim_id)
        print(f"{claim_id}: {state}")
    return "\n".join(
        f"{label}: {len(ids)} ({', '.join(ids)})"
        for label, ids in sorted(results.items())
    )


def main(argv: list[str]) -> str:
    """Work the claim named in argv, or every waiting claim."""
    if argv:
        claim_ids = argv
    else:
        queue = call("GET", "/api/claims")
        claim_ids = [row["claim_id"] for row in queue if row["state"] == "waiting"]
    if not claim_ids:
        return "No claims are waiting."
    return work_queue(claim_ids, run)


if __name__ == "__main__":
    print(main(sys.argv[1:]))
