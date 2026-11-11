"""Request and response models for the API."""

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

State = Literal["waiting", "in_progress", "waiting_for_sign_off", "decided"]
Outcome = Literal["approve", "decline", "refer"]
StepKind = Literal["read", "reasoning", "decision", "payment", "error"]


class QueueRow(BaseModel):
    claim_id: str
    customer_name: str
    claim_type: str
    submitted_on: str
    amount_claimed: str
    state: State
    outcome: Outcome | None


class Item(BaseModel):
    description: str
    category: str
    amount: str


class Document(BaseModel):
    name: str
    type: str
    content: str


class Section(BaseModel):
    number: int
    title: str


class Decision(BaseModel):
    outcome: Outcome
    payout: str
    calculation: str
    explanation: str
    sections: list[Section]
    decided_at: str


class SignOff(BaseModel):
    handler_id: str
    handler_name: str
    signed_at: str


class Payment(BaseModel):
    amount: str
    paid_at: str


class Claim(BaseModel):
    claim_id: str
    policy_id: str
    customer_id: str
    customer_name: str
    claim_type: str
    submitted_on: str
    incident_date: str
    incident_location: str
    summary: str
    story: str
    items: list[Item]
    amount_claimed: str
    documents: list[Document]
    state: State
    decision: Decision | None
    sign_off: SignOff | None
    payment: Payment | None


class Plan(BaseModel):
    plan: str
    name: str
    trip_cancellation_max: str
    trip_delay_waiting_hours: int
    trip_delay_max: str
    baggage_delay_waiting_hours: int
    baggage_delay_max: str
    baggage_max: str
    per_item_limit: str
    passport_max: str
    emergency_medical_max: str
    deductible: str


class Policy(BaseModel):
    policy_id: str
    customer_id: str
    plan: Plan
    add_ons: list[str]
    purchased_on: str
    sold_through: str
    destination: str
    departs_on: str
    returns_on: str
    trip_cost: str
    travelers: list[str]
    status: str


class PreviousClaim(BaseModel):
    claim_id: str
    filed_on: str
    incident_date: str
    claim_type: str
    summary: str
    outcome: str
    amount_paid: str


class Customer(BaseModel):
    customer_id: str
    name: str
    customer_since: str
    previous_claims: list[PreviousClaim]


class PolicyWording(BaseModel):
    text: str
    sections: list[Section]


class Instructions(BaseModel):
    text: str


class Handler(BaseModel):
    handler_id: str
    name: str
    role: str
    can_approve_over_limit: bool


class Step(BaseModel):
    id: int
    run_id: str
    kind: StepKind
    content: str
    created_at: str


class StartRequest(BaseModel):
    run_id: str = Field(min_length=1)


class DecisionRequest(BaseModel):
    run_id: str = Field(min_length=1)
    outcome: Outcome
    payout: Decimal
    calculation: str = Field(min_length=1, max_length=600)
    explanation: str = Field(min_length=1, max_length=600)
    sections: list[int] = Field(min_length=1)


class PaymentRequest(BaseModel):
    amount: Decimal


class SignOffRequest(BaseModel):
    handler_id: str


class FailRequest(BaseModel):
    run_id: str
    error: str


class StepRequest(BaseModel):
    run_id: str
    kind: StepKind
    content: str
