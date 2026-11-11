"""T6, FND-02/17/20: approved diagnostic wire contract."""

import json
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError
from resume_core.contracts import (
    DeliveryWarning,
    DiagnosticCreate,
    DiagnosticError,
    DiagnosticExecution,
    DiagnosticResponse,
    DiagnosticResult,
)


def payload(**changes):
    value = {
        "id": str(uuid4()),
        "requestId": str(uuid4()),
        "idempotencyKey": str(uuid4()),
        "status": "pending",
        "attemptCount": 0,
        "createdAt": "2026-11-11T12:00:00Z",
        "updatedAt": "2026-11-11T12:00:00Z",
        "result": None,
        "error": None,
        "deliveryWarning": None,
    }
    return value | changes


def test_request_only_accepts_opaque_uuid_key():
    key = str(uuid4())
    request = DiagnosticCreate.model_validate_json(json.dumps({"idempotencyKey": key}))
    assert request.model_dump(mode="json") == {"idempotencyKey": key}


@pytest.mark.parametrize(
    "value",
    [
        {},
        {"idempotencyKey": "bad"},
        {"idempotencyKey": 123},
        {"idempotency_key": str(uuid4())},
        {"idempotencyKey": str(uuid4()), "fixture": "other"},
    ],
)
def test_invalid_request_contract_rejected(value):
    with pytest.raises(ValidationError):
        DiagnosticCreate.model_validate_json(json.dumps(value))


def test_execution_roundtrips_every_approved_field():
    value = payload()
    execution = DiagnosticExecution.model_validate_json(json.dumps(value))
    assert execution.model_dump(mode="json") == value
    assert set(execution.model_dump()) == set(value)


@pytest.mark.parametrize("field", ["id", "requestId", "idempotencyKey"])
def test_identifiers_are_uuids(field):
    with pytest.raises(ValidationError):
        DiagnosticExecution.model_validate_json(json.dumps(payload(**{field: "bad"})))


@pytest.mark.parametrize("count", [-1, 4, True, "1", 1.2])
def test_attempt_count_is_strict_integer_in_zero_to_three(count):
    with pytest.raises(ValidationError):
        DiagnosticExecution.model_validate_json(json.dumps(payload(attemptCount=count)))


@pytest.mark.parametrize("count", [0, 1, 2, 3])
def test_valid_attempt_budget(count):
    assert DiagnosticExecution.model_validate(payload(attemptCount=count)).attempt_count == count


@pytest.mark.parametrize("status", ["pending", "queued", "running"])
def test_active_states_allow_only_null_result_and_terminal_error(status):
    execution = DiagnosticExecution.model_validate(payload(status=status))
    assert execution.result is None and execution.error is None
    with pytest.raises(ValidationError):
        DiagnosticExecution.model_validate(
            payload(
                status=status, result={"message": "diagnostic_completed", "fixtureVersion": "m0-v1"}
            )
        )


def test_succeeded_fixture_is_exact_and_warning_cleared():
    result = {"message": "diagnostic_completed", "fixtureVersion": "m0-v1"}
    execution = DiagnosticExecution.model_validate(
        payload(status="succeeded", attemptCount=1, result=result)
    )
    assert execution.model_dump(mode="json")["result"] == result
    assert execution.error is None and execution.delivery_warning is None
    with pytest.raises(ValidationError):
        DiagnosticExecution.model_validate(payload(status="succeeded"))
    with pytest.raises(ValidationError):
        DiagnosticExecution.model_validate(
            payload(status="succeeded", result=result, deliveryWarning=DeliveryWarning())
        )


def test_failed_requires_constant_error_and_no_result():
    error = DiagnosticError.for_code("deadline_exceeded")
    execution = DiagnosticExecution.model_validate(payload(status="failed", error=error))
    assert execution.error.code == "deadline_exceeded"
    assert execution.result is None and execution.delivery_warning is None
    with pytest.raises(ValidationError):
        DiagnosticExecution.model_validate(payload(status="failed"))
    with pytest.raises(ValidationError):
        DiagnosticExecution.model_validate(
            payload(status="failed", error=error, result=DiagnosticResult())
        )


@pytest.mark.parametrize("value", ["unknown", "done", 1, None])
def test_unknown_state_rejected(value):
    with pytest.raises(ValidationError):
        DiagnosticExecution.model_validate(payload(status=value))


def test_utc_normalization_and_naive_rejection():
    execution = DiagnosticExecution.model_validate(payload(createdAt="2026-11-11T09:00:00-03:00"))
    assert execution.created_at == datetime(2026, 11, 11, 12, tzinfo=UTC)
    assert execution.model_dump(mode="json")["createdAt"] == "2026-11-11T12:00:00Z"
    with pytest.raises(ValidationError):
        DiagnosticExecution.model_validate(payload(createdAt="2026-11-11T12:00:00"))
    with pytest.raises(ValidationError):
        DiagnosticExecution.model_validate(payload(updatedAt=1794398400))


def test_transient_warning_is_separate_from_terminal_error():
    execution = DiagnosticExecution.model_validate(payload(deliveryWarning=DeliveryWarning()))
    assert execution.model_dump(mode="json")["deliveryWarning"] == {
        "code": "queue_unavailable",
        "message": "Queue is temporarily unavailable.",
    }
    assert execution.error is None


@pytest.mark.parametrize(
    "model,value",
    [
        (DiagnosticResult, {"message": "invented", "fixtureVersion": "m0-v1"}),
        (DiagnosticResult, {"fixtureVersion": "m0-v2"}),
        (DeliveryWarning, {"message": "SYNTHETIC_SECRET"}),
        (DiagnosticError, {"code": "deadline_exceeded", "message": "SYNTHETIC_SECRET"}),
        (DiagnosticError, {"code": "arbitrary", "message": "SYNTHETIC_SECRET"}),
    ],
)
def test_results_and_messages_are_allowlisted(model, value):
    with pytest.raises(ValidationError):
        model.model_validate(value)


def test_extra_fields_and_internal_lease_are_not_wire_contract():
    with pytest.raises(ValidationError):
        DiagnosticExecution.model_validate(payload(leaseToken="SYNTHETIC_SECRET"))
    with pytest.raises(ValidationError):
        DiagnosticResult.model_validate({"private": "SYNTHETIC_SECRET"})


def test_latest_empty_is_nullable_envelope():
    assert DiagnosticResponse(execution=None).model_dump(mode="json") == {"execution": None}


def test_json_schema_uses_camelcase_and_rejects_extra_properties():
    schema = DiagnosticCreate.model_json_schema()
    assert set(schema["properties"]) == {"idempotencyKey"}
    assert schema["additionalProperties"] is False
    execution = DiagnosticExecution.model_json_schema()["properties"]
    assert execution["attemptCount"]["minimum"] == 0
    assert execution["attemptCount"]["maximum"] == 3
    assert execution["id"]["format"] == "uuid"


@pytest.mark.parametrize("status", ["pending", "queued", "running"])
def test_active_states_reject_terminal_error(status):
    with pytest.raises(ValidationError):
        DiagnosticExecution.model_validate(
            payload(status=status, error=DiagnosticError.for_code("internal_error"))
        )


def test_succeeded_rejects_terminal_error():
    with pytest.raises(ValidationError):
        DiagnosticExecution.model_validate(
            payload(
                status="succeeded",
                result=DiagnosticResult(),
                error=DiagnosticError.for_code("internal_error"),
            )
        )


def test_failed_rejects_transient_warning():
    with pytest.raises(ValidationError):
        DiagnosticExecution.model_validate(
            payload(
                status="failed",
                error=DiagnosticError.for_code("internal_error"),
                deliveryWarning=DeliveryWarning(),
            )
        )


@pytest.mark.parametrize(
    "code,message",
    [
        ("deadline_exceeded", "Diagnostic deadline exceeded."),
        ("attempts_exhausted", "Diagnostic attempts exhausted."),
        ("internal_error", "Diagnostic could not be completed."),
    ],
)
def test_terminal_messages_are_exact_for_each_code(code, message):
    assert DiagnosticError.for_code(code).model_dump() == {"code": code, "message": message}


def test_valid_but_mismatched_error_message_is_rejected():
    with pytest.raises(ValidationError):
        DiagnosticError(code="deadline_exceeded", message="Diagnostic attempts exhausted.")
