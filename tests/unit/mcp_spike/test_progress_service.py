"""SPIKE-06/08/09/10/11/15/18/20: authorized progress reporting."""

from unittest.mock import Mock

import pytest
from pydantic import ValidationError
from resume_core.mcp_spike.contracts import ProgressReport, Receipt
from resume_core.mcp_spike.policy import Profile
from resume_core.mcp_spike.repository import Conflict, TemporarilyUnavailable
from resume_core.mcp_spike.service import ProgressService
from resume_core.service import PermissionDenied

RECEIPT_ID = "10000000-0000-4000-8000-000000000001"


def profile(
    client="hermes", capabilities=("application_progress:write",), applications=("app-demo",)
):
    return Profile(client_id=client, application_ids=applications, capabilities=capabilities)


def report(event="form_filled"):
    return ProgressReport(
        application_id="app-demo", execution_id="exec", idempotency_key="key", event=event
    )


@pytest.mark.parametrize("client", ["hermes", "codex"])
def test_allowed_report_uses_profile_identity_and_returns_reported_receipt(client):
    result = Receipt(receipt_id=RECEIPT_ID, confirmation_state="reported_by_agent")
    repo = Mock()
    repo.record.return_value = result
    request = report()
    actual = ProgressService(repo).report(profile(client), request)
    assert actual.model_dump(by_alias=True) == {
        "receiptId": RECEIPT_ID,
        "confirmationState": "reported_by_agent",
    }
    repo.record.assert_called_once_with(client, request)


@pytest.mark.parametrize("principal", [None, profile(capabilities=()), profile(applications=())])
def test_denial_precedes_repository_access(principal):
    repo = Mock()
    with pytest.raises(PermissionDenied):
        ProgressService(repo).report(principal, report())
    repo.record.assert_not_called()


@pytest.mark.parametrize("extra", [{"clientId": "codex"}, {"confirmationState": "confirmed"}])
def test_untrusted_identity_and_confirmation_are_rejected_before_repository(extra):
    repo = Mock()
    payload = report().model_dump(by_alias=True) | extra
    with pytest.raises(ValidationError):
        request = ProgressReport.model_validate(payload)
        ProgressService(repo).report(profile(), request)
    repo.record.assert_not_called()


@pytest.mark.parametrize("error", [Conflict, TemporarilyUnavailable])
def test_repository_errors_propagate_without_success(error):
    repo = Mock()
    repo.record.side_effect = error
    with pytest.raises(error):
        ProgressService(repo).report(profile(), report())


def test_replay_returns_original_receipt():
    original = Receipt(receipt_id=RECEIPT_ID, confirmation_state="reported_by_agent")
    repo = Mock()
    repo.record.return_value = original
    service = ProgressService(repo)
    assert service.report(profile(), report()) == original
    assert service.report(profile(), report()) == original


def test_out_of_scope_application_denied_before_repository():
    repo = Mock()
    request = ProgressReport(
        application_id="other", execution_id="exec", idempotency_key="key", event="started"
    )
    with pytest.raises(PermissionDenied):
        ProgressService(repo).report(profile(), request)
    repo.record.assert_not_called()
