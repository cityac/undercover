"""The UnderCover Agent."""

import json
import os
from typing import Any

import httpx
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, SecretStr

load_dotenv(override=True)

BACKEND_URL = "http://localhost:8000"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "openai/gpt-6-luna"
STEP_LIMIT = 2000
TOOL_KINDS = {"record_decision": "decision", "pay_claim": "payment"}


def backend() -> httpx.Client:
    """Return a client for the UnderCover backend."""
    return httpx.Client(base_url=BACKEND_URL, timeout=30)


def call(method: str, path: str, body: dict[str, Any] | None = None) -> Any:
    """Call the backend; return the JSON, or text the model can act on for a 4xx."""
    with backend() as client:
        response = client.request(method, path, json=body)
    if response.status_code == httpx.codes.NOT_FOUND:
        return f"Not found: {response.json()['detail']}"
    if response.status_code in {409, 422}:
        return f"Refused: {response.json()['detail']}"
    response.raise_for_status()
    return response.json()


def as_text(value: Any) -> str:
    """Return a tool result as text for the model."""
    return value if isinstance(value, str) else json.dumps(value)


@tool
def get_claim(claim_id: str) -> str:
    """Get a claim: the story, items, amounts, documents and its current state."""
    return as_text(call("GET", f"/api/claims/{claim_id}"))


@tool
def get_policy(policy_id: str) -> str:
    """Get a policy with its plan's limits, waiting periods and deductible."""
    return as_text(call("GET", f"/api/policies/{policy_id}"))


@tool
def get_customer(customer_id: str) -> str:
    """Get a customer's name and earlier claims."""
    return as_text(call("GET", f"/api/customers/{customer_id}"))


@tool
def get_policy_wording() -> str:
    """Get the full policy wording with its numbered sections."""
    return as_text(call("GET", "/api/policy-wording")["text"])


class DecisionArgs(BaseModel):
    """Your decision on a claim, recorded once."""

    claim_id: str
    outcome: str = Field(description="approve, decline or refer")
    payout: str = Field(description="dollars such as 420.00; 0.00 unless approve")
    calculation: str = Field(description="how the payout was reached, in a line")
    explanation: str = Field(description="two or three sentences")
    sections: list[int] = Field(description="policy wording section numbers")


def make_record_decision(run_id: str) -> Any:
    """Return the record_decision tool bound to one run."""

    @tool(args_schema=DecisionArgs)
    def record_decision(**fields: Any) -> str:
        """Record your decision on a claim, once, with its reasons."""
        claim_id = fields.pop("claim_id")
        body = {"run_id": run_id, **fields}
        return as_text(call("POST", f"/api/claims/{claim_id}/decision", body))

    return record_decision


@tool
def pay_claim(claim_id: str, amount: str) -> str:
    """Pay the approved payout of a claim, in dollars such as 420.00."""
    return as_text(call("POST", f"/api/claims/{claim_id}/payment", {"amount": amount}))


def tools(run_id: str) -> list[Any]:
    """Return the agent's tools: reading, recording a decision and paying."""
    return [
        get_claim,
        get_policy,
        get_customer,
        get_policy_wording,
        make_record_decision(run_id),
        pay_claim,
    ]


def model() -> ChatOpenAI:
    """Return the model named in MODEL_NAME, or GPT-6 Luna by default."""
    name = os.getenv("MODEL_NAME")
    return ChatOpenAI(
        model=name or DEFAULT_MODEL,
        base_url=OPENROUTER_BASE_URL,
        api_key=SecretStr(os.environ["OPENROUTER_API_KEY"]),
        reasoning_effort=None if name else "low",
    )


def add_step(claim_id: str, run_id: str, kind: str, content: str) -> None:
    """Record one step of the agent's work on the claim."""
    body = {"run_id": run_id, "kind": kind, "content": content[:STEP_LIMIT]}
    call("POST", f"/api/claims/{claim_id}/steps", body)


def record_messages(
    claim_id: str, run_id: str, messages: list[Any], kinds: dict[str, str]
) -> None:
    """Record the model's text, its tool calls and their results as steps."""
    for message in messages:
        if isinstance(message, AIMessage):
            if message.text:
                add_step(claim_id, run_id, "reasoning", message.text)
            for call_ in message.tool_calls:
                kind = TOOL_KINDS.get(call_["name"], "read")
                kinds[call_["id"] or ""] = kind
                add_step(
                    claim_id,
                    run_id,
                    kind,
                    f"{call_['name']}({json.dumps(call_['args'])})",
                )
        elif isinstance(message, ToolMessage):
            kind = kinds.get(message.tool_call_id, "read")
            add_step(claim_id, run_id, kind, f"{message.name}: {message.text}")


def work(claim_id: str, run_id: str, llm: BaseChatModel) -> None:
    """Let the agent work the claim, recording each step."""
    instructions = call("GET", "/api/instructions")["text"]
    agent = create_agent(llm, tools=tools(run_id), system_prompt=instructions)
    kinds: dict[str, str] = {}
    for update in agent.stream(
        {"messages": [{"role": "user", "content": f"Work claim {claim_id}."}]},
        config={"configurable": {"thread_id": run_id}},
        stream_mode="updates",
    ):
        for node in update.values():
            record_messages(claim_id, run_id, (node or {}).get("messages", []), kinds)


def fail(claim_id: str, run_id: str, error: str) -> None:
    """Return the claim to the queue after a failed run."""
    call("POST", f"/api/claims/{claim_id}/fail", {"run_id": run_id, "error": error})


def run(claim_id: str, thread_id: str, llm: BaseChatModel | None = None) -> str:
    """Run the agent on one claim and return the claim's state at the end."""
    started = call("POST", f"/api/claims/{claim_id}/start", {"run_id": thread_id})
    if isinstance(started, str):
        return started
    try:
        work(claim_id, thread_id, llm or model())
    except Exception as error:
        fail(claim_id, thread_id, f"The run failed: {error}")
        return "waiting"
    state = call("GET", f"/api/claims/{claim_id}")["state"]
    if state == "in_progress":
        fail(claim_id, thread_id, "The run ended before the claim was decided and paid")
        return "waiting"
    return state
