"""Approved synthetic diagnostic DTOs; OpenAPI is the TypeScript source of truth."""

from datetime import UTC, datetime
from typing import Literal, Self
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator, model_validator
from pydantic.alias_generators import to_camel

DiagnosticStatus = Literal["pending", "queued", "running", "succeeded", "failed"]
ErrorCode = Literal["deadline_exceeded", "attempts_exhausted", "internal_error"]
ERROR_MESSAGES: dict[str, str] = {
    "deadline_exceeded": "Diagnostic deadline exceeded.",
    "attempts_exhausted": "Diagnostic attempts exhausted.",
    "internal_error": "Diagnostic could not be completed.",
}


class Contract(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        alias_generator=to_camel,
        validate_by_name=True,
        serialize_by_alias=True,
        frozen=True,
        validate_default=True,
    )


class DiagnosticCreate(Contract):
    model_config = ConfigDict(validate_by_name=False)
    idempotency_key: UUID


class DiagnosticResult(Contract):
    message: Literal["diagnostic_completed"] = "diagnostic_completed"
    fixture_version: Literal["m0-v1"] = "m0-v1"


class DeliveryWarning(Contract):
    code: Literal["queue_unavailable"] = "queue_unavailable"
    message: Literal["Queue is temporarily unavailable."] = "Queue is temporarily unavailable."


class DiagnosticError(Contract):
    code: ErrorCode
    message: Literal[
        "Diagnostic deadline exceeded.",
        "Diagnostic attempts exhausted.",
        "Diagnostic could not be completed.",
    ]

    @model_validator(mode="after")
    def validate_message(self) -> Self:
        if self.message != ERROR_MESSAGES[self.code]:
            raise ValueError("error message must match its stable code")
        return self

    @classmethod
    def for_code(cls, code: ErrorCode) -> Self:
        return cls(code=code, message=ERROR_MESSAGES[code])


class DiagnosticExecution(Contract):
    id: UUID
    request_id: UUID
    idempotency_key: UUID
    status: DiagnosticStatus
    attempt_count: int = Field(ge=0, le=3, strict=True)
    created_at: AwareDatetime
    updated_at: AwareDatetime
    result: DiagnosticResult | None = None
    delivery_warning: DeliveryWarning | None = None
    error: DiagnosticError | None = None

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def reject_numeric_time(cls, value):
        if not isinstance(value, (str, datetime)):
            raise ValueError("timestamps must be RFC 3339 strings or aware datetimes")
        return value

    @field_validator("created_at", "updated_at")
    @classmethod
    def normalize_utc(cls, value: datetime) -> datetime:
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def validate_state(self) -> Self:
        if self.status == "succeeded":
            valid = self.result is not None and self.error is None and self.delivery_warning is None
        elif self.status == "failed":
            valid = self.error is not None and self.result is None and self.delivery_warning is None
        else:
            valid = self.result is None and self.error is None
        if not valid:
            raise ValueError("diagnostic state has inconsistent result, error or warning")
        return self


class DiagnosticResponse(Contract):
    execution: DiagnosticExecution | None
