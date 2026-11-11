"""The UnderCover backend."""

import sqlite3
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from backend import claims, models
from backend.db import connect, create_schema, is_empty
from backend.seed import seed


def prepare() -> None:
    """Create the store, and load the records if it is empty."""
    conn = connect()
    create_schema(conn)
    if is_empty(conn):
        seed(conn)
    conn.close()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Prepare the store when the backend starts."""
    prepare()
    yield


app = FastAPI(title="UnderCover", lifespan=lifespan)


def database() -> Iterator[sqlite3.Connection]:
    """Open a connection for one request."""
    conn = connect()
    try:
        yield conn
    finally:
        conn.close()


Db = Annotated[sqlite3.Connection, Depends(database)]


@app.exception_handler(claims.NotFoundError)
def not_found(_: Request, error: claims.NotFoundError) -> JSONResponse:
    """Answer 404 for a record that does not exist."""
    return JSONResponse({"detail": str(error)}, status_code=404)


@app.exception_handler(claims.RefusedError)
def refused(_: Request, error: claims.RefusedError) -> JSONResponse:
    """Answer 409 for a move the rules do not allow."""
    return JSONResponse({"detail": str(error)}, status_code=409)


@app.get("/api/health", operation_id="health")
def health() -> dict[str, str]:
    """Check that the backend is running."""
    return {"status": "ok"}


@app.get("/api/claims", operation_id="list_claims")
def list_claims(conn: Db) -> list[models.QueueRow]:
    """List the claims queue in claim order."""
    return claims.list_queue(conn)


@app.get("/api/claims/{claim_id}", operation_id="get_claim")
def get_claim(claim_id: str, conn: Db) -> models.Claim:
    """Get one claim in full, with its decision, sign-off and payment."""
    return claims.get_claim(conn, claim_id)


@app.get("/api/claims/{claim_id}/steps", operation_id="list_steps")
def list_steps(claim_id: str, conn: Db) -> list[models.Step]:
    """List the agent's steps on a claim in order."""
    return claims.list_steps(conn, claim_id)


@app.get("/api/policies/{policy_id}", operation_id="get_policy")
def get_policy(policy_id: str, conn: Db) -> models.Policy:
    """Get one policy with its plan."""
    return claims.get_policy(conn, policy_id)


@app.get("/api/customers/{customer_id}", operation_id="get_customer")
def get_customer(customer_id: str, conn: Db) -> models.Customer:
    """Get a customer's name and claim history."""
    return claims.get_customer(conn, customer_id)


@app.get("/api/policy-wording", operation_id="get_policy_wording")
def get_policy_wording(conn: Db) -> models.PolicyWording:
    """Get the policy wording and its numbered sections."""
    return claims.get_policy_wording(conn)


@app.get("/api/handlers", operation_id="list_handlers")
def list_handlers(conn: Db) -> list[models.Handler]:
    """List the claims handlers."""
    return claims.list_handlers(conn)


@app.get("/api/instructions", operation_id="get_instructions")
def get_instructions() -> models.Instructions:
    """Get the agent's instructions, read only."""
    return claims.get_instructions()


@app.post("/api/claims/{claim_id}/start", operation_id="start_claim")
def start_claim(claim_id: str, body: models.StartRequest, conn: Db) -> models.Claim:
    """Take a waiting claim for an agent run."""
    return claims.start(conn, claim_id, body.run_id)


@app.post("/api/claims/{claim_id}/decision", operation_id="record_decision")
def record_decision(
    claim_id: str, body: models.DecisionRequest, conn: Db
) -> models.Claim:
    """Record the agent's decision on a claim in progress."""
    return claims.record_decision(conn, claim_id, body)


@app.post("/api/claims/{claim_id}/payment", operation_id="pay_claim")
def pay_claim(claim_id: str, body: models.PaymentRequest, conn: Db) -> models.Claim:
    """Pay the approved payout of a claim."""
    return claims.pay(conn, claim_id, body.amount)


@app.post("/api/claims/{claim_id}/sign-off", operation_id="sign_off_claim")
def sign_off_claim(
    claim_id: str, body: models.SignOffRequest, conn: Db
) -> models.Claim:
    """Sign off a payout over the limit and pay it."""
    return claims.sign_off(conn, claim_id, body.handler_id)


@app.post("/api/claims/{claim_id}/fail", operation_id="fail_claim")
def fail_claim(claim_id: str, body: models.FailRequest, conn: Db) -> models.Claim:
    """Undo a failed agent run and return the claim to the queue."""
    return claims.fail(conn, claim_id, body)


@app.post("/api/claims/{claim_id}/steps", operation_id="add_step")
def add_step(claim_id: str, body: models.StepRequest, conn: Db) -> models.Step:
    """Record one of the agent's steps on a claim."""
    return claims.add_step(conn, claim_id, body)
