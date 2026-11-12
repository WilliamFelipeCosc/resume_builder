import pytest
from pydantic import ValidationError
from resume_core.mcp_spike.contracts import (
    ApplicationContext,
    ContextQuery,
    Envelope,
    FormValues,
    ProgressReport,
    Receipt,
    check_json_size,
)


@pytest.mark.parametrize("value", ["a", "a" * 128, "a.Z_:-09"])
def test_valid_identifiers(value):
    assert ContextQuery.model_validate({"applicationId": value}).model_dump(by_alias=True) == {
        "applicationId": value
    }


@pytest.mark.parametrize("value", ["", "a" * 129, "á", "a/b", "a b", 3, None, True])
def test_invalid_identifiers(value):
    with pytest.raises(ValidationError):
        ContextQuery.model_validate({"applicationId": value})


@pytest.mark.parametrize("event", ["started", "form_filled", "blocked"])
def test_valid_events(event):
    payload = dict(applicationId="a", executionId="e", idempotencyKey="k", event=event)
    assert ProgressReport.model_validate(payload).model_dump(by_alias=True) == payload


@pytest.mark.parametrize("event", ["submitted", "confirmed", 1])
def test_invalid_events(event):
    with pytest.raises(ValidationError):
        ProgressReport.model_validate(
            dict(applicationId="a", executionId="e", idempotencyKey="k", event=event)
        )


def test_extra_argument_rejected():
    with pytest.raises(ValidationError):
        ContextQuery.model_validate({"applicationId": "a", "clientId": "codex"})


@pytest.mark.parametrize("length,valid", [(2000, True), (2001, False)])
def test_form_text_limit(length, valid):
    payload = dict(fullName="x" * length, email="e", targetRole="r", approvedAnswer="a")
    if valid:
        assert FormValues.model_validate(payload).full_name == "x" * length
    else:
        with pytest.raises(ValidationError):
            FormValues.model_validate(payload)


@pytest.mark.parametrize("limit", [4096, 16384])
def test_json_byte_boundaries(limit):
    assert check_json_size({"x": "a" * (limit - 8)}, limit) == limit
    with pytest.raises(ValueError):
        check_json_size({"x": "a" * (limit - 7)}, limit)


def test_json_counts_utf8_bytes():
    assert check_json_size({"x": "é"}, 10) == 10
    with pytest.raises(ValueError):
        check_json_size({"x": "é"}, 9)


def test_context_and_envelope_roundtrip():
    context = {
        "applicationId": "app-demo",
        "jobSnapshotId": "job-demo",
        "resumeRevisionId": "resume-demo",
        "approvedAnswers": ["answer"],
        "evidenceRefs": ["evidence-demo"],
        "restrictions": ["fictional"],
        "formValues": {
            "fullName": "name",
            "email": "email",
            "targetRole": "role",
            "approvedAnswer": "answer",
        },
    }
    payload = {
        "schemaVersion": "m05.v1",
        "data": context,
        "provenance": [{"sourceId": "fixture", "version": "v1"}],
        "truncated": False,
        "policy": {
            "clientId": "codex",
            "applicationId": "app-demo",
            "capabilities": ["application_context:read"],
        },
        "requestId": "12345678-1234-4234-8234-123456789abc",
    }
    result = Envelope[ApplicationContext].model_validate(payload)
    assert result.model_dump(by_alias=True) == payload


def test_receipt_envelope_roundtrip():
    payload = {
        "schemaVersion": "m05.v1",
        "data": {
            "receiptId": "12345678-1234-4234-8234-123456789abc",
            "confirmationState": "reported_by_agent",
        },
        "provenance": [],
        "truncated": False,
        "policy": {
            "clientId": "codex",
            "applicationId": "app-demo",
            "capabilities": ["application_progress:write"],
        },
        "requestId": "12345678-1234-4234-8234-123456789abc",
    }
    assert Envelope[Receipt].model_validate(payload).model_dump(by_alias=True) == payload


def test_confirmed_receipt_is_rejected():
    with pytest.raises(ValidationError):
        Receipt.model_validate(
            {"receiptId": "12345678-1234-4234-8234-123456789abc", "confirmationState": "confirmed"}
        )


def test_invalid_receipt_uuid_is_rejected():
    with pytest.raises(ValidationError):
        Receipt.model_validate({"receiptId": "bad", "confirmationState": "reported_by_agent"})


def test_oversized_envelope_rejected():
    payload = {
        "schemaVersion": "m05.v1",
        "data": {
            "applicationId": "app-demo",
            "jobSnapshotId": "job-demo",
            "resumeRevisionId": "resume-demo",
            "approvedAnswers": ["x" * 16384],
            "evidenceRefs": [],
            "restrictions": [],
            "formValues": {"fullName": "n", "email": "e", "targetRole": "r", "approvedAnswer": "a"},
        },
        "provenance": [],
        "truncated": False,
        "policy": {"clientId": "codex", "applicationId": "app-demo", "capabilities": []},
        "requestId": "12345678-1234-4234-8234-123456789abc",
    }
    with pytest.raises(ValidationError):
        Envelope[ApplicationContext].model_validate(payload)
