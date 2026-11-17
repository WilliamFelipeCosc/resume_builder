"""Stable, non-reflecting HTTP error contracts."""

from typing import Literal

from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

ErrorCode = Literal[
    "unauthorized",
    "forbidden_origin",
    "forbidden",
    "not_found",
    "active_diagnostic",
    "stale_revision",
    "idempotency_conflict",
    "dependent_changes",
    "missing_candidate_dependency",
    "body_too_large",
    "unsupported_media_type",
    "invalid_request",
    "rate_limited",
    "storage_unavailable",
    "database_busy",
    "internal_error",
]

ERRORS = {
    401: ("unauthorized", "Open the application using the local command."),
    403: ("forbidden_origin", "Local origin is required."),
    404: ("not_found", "Resource not found."),
    409: ("active_diagnostic", "A diagnostic is already active."),
    413: ("body_too_large", "Request body exceeds the allowed limit."),
    415: ("unsupported_media_type", "Unsupported media type."),
    422: ("invalid_request", "Request does not match the contract."),
    429: ("rate_limited", "Request limit reached."),
    503: ("storage_unavailable", "Service is temporarily unavailable."),
    500: ("internal_error", "Request could not be completed."),
}

MESSAGES = {code: message for code, message in ERRORS.values()} | {
    "forbidden": "Operation is not permitted.",
    "stale_revision": "The revision is no longer current.",
    "idempotency_conflict": "The idempotency key conflicts with an earlier request.",
    "dependent_changes": "Dependent changes prevent this operation.",
    "missing_candidate_dependency": "A required candidate is missing.",
    "database_busy": "Service is temporarily unavailable.",
}


FieldPath = Literal[
    "ticket",
    "idempotency_key",
    "idempotencyKey",
    "baseRevisionId",
    "full_name",
    "professional_headline",
    "email",
    "phone_original",
    "objective_original",
    "city_of_residence",
    "country_of_residence",
    "linkedin_url",
    "github_url",
    "company_name_original",
    "job_title_original",
    "start_date_original",
    "end_date_original",
    "start_period",
    "end_period",
    "end_date_is_current_as_of_source",
    "location",
    "text_original",
    "text_current",
    "statement_type",
    "title",
    "text",
    "title_is_generated_label",
    "description_original",
    "description_current",
    "time_to_develop_original",
    "metric_type",
    "metric_value",
    "metric_unit",
    "metric_meaning",
    "name",
    "original_labels",
    "category",
    "explicitly_listed_in_skills_section",
    "institution",
    "program_original",
    "ongoing_as_of_source_document",
    "currently_ongoing",
    "language",
    "proficiency_original",
    "description",
    "evidence_kind",
    "source_document_id",
    "page",
]
SAFE_FIELD_PATHS = frozenset(FieldPath.__args__)


class FieldError(BaseModel):
    model_config = ConfigDict(extra="forbid")
    path: FieldPath
    code: Literal["invalid"] = "invalid"


class HttpError(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: ErrorCode
    message: str
    requestId: str
    fieldErrors: list[FieldError] | None = None


class HttpErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    error: HttpError


def error_response(
    status: int, request_id: str, *, code: ErrorCode | None = None, fields: tuple[str, ...] = ()
) -> JSONResponse:
    selected = code or ERRORS[status][0]
    safe_fields = [FieldError(path=path) for path in fields if path in SAFE_FIELD_PATHS]
    error = HttpError(
        code=selected,
        message=MESSAGES[selected],
        requestId=request_id,
        fieldErrors=safe_fields or None,
    )
    return JSONResponse(
        HttpErrorResponse(error=error).model_dump(exclude_none=True), status_code=status
    )
