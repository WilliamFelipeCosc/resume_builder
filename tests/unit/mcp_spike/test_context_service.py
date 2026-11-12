"""SPIKE-02/03/04/18/19: authorized synthetic context service."""

import json
from pathlib import Path
from unittest.mock import Mock

import pytest
from resume_core.mcp_spike.contracts import ApplicationContext, ContextQuery
from resume_core.mcp_spike.policy import Profile
from resume_core.mcp_spike.service import ContextNotFound, ContextService
from resume_core.service import PermissionDenied

FIXTURE = Path(__file__).resolve().parents[3] / "data/synthetic/mcp-spike/context.json"


def profile(capabilities=("application_context:read",), application_ids=("app-demo",)):
    return Profile(client_id="hermes", application_ids=application_ids, capabilities=capabilities)


def test_authorized_result_matches_complete_versioned_fixture():
    payload = json.loads(FIXTURE.read_text())
    loader = Mock(return_value=ApplicationContext.model_validate(payload))
    result = ContextService(loader).get(profile(), ContextQuery(application_id="app-demo"))
    assert result.model_dump(by_alias=True) == payload
    loader.assert_called_once_with("app-demo")


@pytest.mark.parametrize("principal", [None, profile(capabilities=()), profile(application_ids=())])
def test_denial_precedes_any_fixture_retrieval(principal):
    loader = Mock()
    with pytest.raises(PermissionDenied):
        ContextService(loader).get(principal, ContextQuery(application_id="app-demo"))
    loader.assert_not_called()


def test_ungranted_application_denied_without_retrieval():
    loader = Mock()
    with pytest.raises(PermissionDenied):
        ContextService(loader).get(profile(), ContextQuery(application_id="other"))
    loader.assert_not_called()


def test_granted_missing_fixture_is_not_invented():
    loader = Mock(return_value=None)
    with pytest.raises(ContextNotFound):
        ContextService(loader).get(profile(), ContextQuery(application_id="app-demo"))
    loader.assert_called_once_with("app-demo")


def test_mismatched_fixture_is_not_exposed():
    payload = json.loads(FIXTURE.read_text()) | {"applicationId": "other"}
    loader = Mock(return_value=ApplicationContext.model_validate(payload))
    with pytest.raises(ContextNotFound):
        ContextService(loader).get(profile(), ContextQuery(application_id="app-demo"))


@pytest.mark.parametrize("client", ["hermes", "codex"])
def test_both_authorized_profiles_receive_fixture(client):
    context = ApplicationContext.model_validate_json(FIXTURE.read_text())
    principal = Profile(
        client_id=client, application_ids=("app-demo",), capabilities=("application_context:read",)
    )
    assert (
        ContextService(lambda _: context).get(principal, ContextQuery(application_id="app-demo"))
        == context
    )
