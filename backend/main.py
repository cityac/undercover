"""The UnderCover backend."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

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


@app.get("/api/health", operation_id="health")
def health() -> dict[str, str]:
    """Check that the backend is running."""
    return {"status": "ok"}
