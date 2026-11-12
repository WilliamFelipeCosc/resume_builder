"""Strict, transport-independent contracts for the synthetic MCP spike."""

import json
from typing import Annotated, Generic, Literal, Self, TypeVar

from pydantic import BaseModel, ConfigDict, Field, StrictStr, model_validator
from pydantic.alias_generators import to_camel

Identifier = Annotated[
    str, Field(strict=True, min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._:-]+$")
]
Text = Annotated[str, Field(strict=True, max_length=2000)]
UuidText = Annotated[
    str,
    Field(
        strict=True,
        pattern=r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
    ),
]
Event = Literal["started", "form_filled", "blocked"]
Capability = Literal["application_context:read", "application_progress:write"]


class Contract(BaseModel):
    model_config = ConfigDict(
        extra="forbid", alias_generator=to_camel, validate_by_name=True, serialize_by_alias=True
    )


class ContextQuery(Contract):
    application_id: Identifier


class ProgressReport(Contract):
    application_id: Identifier
    execution_id: Identifier
    idempotency_key: Identifier
    event: Event


class FormValues(Contract):
    full_name: Text
    email: Text
    target_role: Text
    approved_answer: Text


class ApplicationContext(Contract):
    application_id: Identifier
    job_snapshot_id: Identifier
    resume_revision_id: Identifier
    approved_answers: list[StrictStr]
    evidence_refs: list[Identifier]
    restrictions: list[StrictStr]
    form_values: FormValues


class Receipt(Contract):
    receipt_id: UuidText
    confirmation_state: Literal["reported_by_agent"]


class Provenance(Contract):
    source_id: Identifier
    version: Identifier


class Policy(Contract):
    client_id: Identifier
    application_id: Identifier
    capabilities: list[Capability]


Data = TypeVar("Data", ApplicationContext, Receipt)


class Envelope(Contract, Generic[Data]):
    schema_version: Literal["m05.v1"]
    data: Data
    provenance: list[Provenance]
    truncated: Literal[False]
    policy: Policy
    request_id: UuidText

    @model_validator(mode="after")
    def enforce_size(self) -> Self:
        check_json_size(self.model_dump(mode="json", by_alias=True), 16384)
        return self


class ErrorDetail(Contract):
    code: Literal[
        "NOT_AUTHORIZED",
        "CONTEXT_NOT_FOUND",
        "SCHEMA_INVALID",
        "CONFLICT",
        "TEMPORARILY_UNAVAILABLE",
        "CONTEXT_TRUNCATED",
        "INTERNAL_ERROR",
    ]
    message: Text


class ErrorEnvelope(Contract):
    schema_version: Literal["m05.v1"]
    error: ErrorDetail
    request_id: UuidText


def check_json_size(value: object, limit: int) -> int:
    size = len(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    if size > limit:
        raise ValueError("JSON exceeds byte limit")
    return size
