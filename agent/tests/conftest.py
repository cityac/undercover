from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

from agent import main
from backend.main import app


class StubModel(GenericFakeChatModel):
    """A chat model that gives scripted replies in place of a real model."""

    def bind_tools(self, tools, **kwargs):
        return self


def stub(*replies: AIMessage) -> StubModel:
    return StubModel(messages=iter(replies))


def calls(*tool_calls: tuple[str, dict], text: str = "") -> AIMessage:
    return AIMessage(
        content=text,
        tool_calls=[
            {"name": name, "args": args, "id": f"{name}-{index}"}
            for index, (name, args) in enumerate(tool_calls)
        ],
    )


@pytest.fixture(autouse=True)
def backend(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    monkeypatch.setenv("UNDERCOVER_DB", str(tmp_path / "agent.db"))
    with TestClient(app) as client:
        monkeypatch.setattr(main, "backend", lambda: TestClient(app))
        yield client
