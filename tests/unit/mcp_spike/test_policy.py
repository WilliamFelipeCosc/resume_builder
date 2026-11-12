import pytest
from pydantic import ValidationError
from resume_core.mcp_spike.policy import Profile, require
from resume_core.service import PermissionDenied


@pytest.mark.parametrize("client", ["hermes", "codex"])
def test_profile_allows_approved_scope(client):
    profile = Profile.model_validate(
        {
            "clientId": client,
            "applicationIds": ["app-demo"],
            "capabilities": ["application_context:read", "application_progress:write"],
        }
    )
    assert profile.client_id == client
    require(profile, "application_context:read", "app-demo")
    require(profile, "application_progress:write", "app-demo")


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"clientId": "hermes", "applicationIds": ["*"], "capabilities": []},
        {"clientId": "hermes", "applicationIds": ["other"], "capabilities": []},
        {"clientId": "hermes", "applicationIds": ["app-demo"], "capabilities": ["*"]},
        {"clientId": "unknown", "applicationIds": ["app-demo"], "capabilities": []},
        {"clientId": "hermes", "applicationIds": ["app-demo"], "capabilities": [], "secret": "x"},
    ],
)
def test_invalid_profiles_rejected(payload):
    with pytest.raises(ValidationError):
        Profile.model_validate(payload)


@pytest.mark.parametrize(
    "application,capability",
    [
        ("other", "application_context:read"),
        ("app-demo", "application_progress:write"),
    ],
)
def test_missing_grant_denied(application, capability):
    profile = Profile.model_validate(
        {
            "clientId": "codex",
            "applicationIds": ["app-demo"],
            "capabilities": ["application_context:read"],
        }
    )
    with pytest.raises(PermissionDenied):
        require(profile, capability, application)


def test_absent_principal_denied():
    with pytest.raises(PermissionDenied):
        require(None, "application_context:read", "app-demo")
