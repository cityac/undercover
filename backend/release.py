"""Free a claim left in progress. Run `uv run -m backend.release CLM-1001`."""

import sys

from backend import claims
from backend.db import connect


def main(argv: list[str]) -> str:
    """Release the claim named in argv and describe the result."""
    if len(argv) != 1:
        return "Usage: uv run -m backend.release CLM-1001"
    conn = connect()
    try:
        claim = claims.release(conn, argv[0])
    except (claims.NotFoundError, claims.RefusedError) as error:
        return f"Not released: {error}"
    finally:
        conn.close()
    return f"{claim.claim_id} is {claim.state} again"


if __name__ == "__main__":
    print(main(sys.argv[1:]))
