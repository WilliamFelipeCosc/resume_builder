import json
import os

import pytest
from resume_core.mcp_spike.policy import load_profile


@pytest.fixture
def config(tmp_path):
    tmp_path.chmod(0o700)
    directory = tmp_path / "profiles"
    directory.mkdir(mode=0o700)
    path = directory / "codex.json"
    path.write_text(
        json.dumps(
            {
                "clientId": "codex",
                "applicationIds": ["app-demo"],
                "capabilities": ["application_context:read"],
            }
        )
    )
    path.chmod(0o600)
    return tmp_path


def test_load_profile(config):
    assert load_profile(config, "codex").client_id == "codex"


def test_missing_profile_fails_closed(config):
    with pytest.raises(ValueError):
        load_profile(config, "hermes")


def test_removed_profile_cannot_restart(config):
    assert load_profile(config, "codex").client_id == "codex"
    (config / "profiles/codex.json").unlink()
    with pytest.raises(ValueError):
        load_profile(config, "codex")


def test_symlink_profiles_directory_rejected(config):
    directory = config / "profiles"
    directory.rename(config / "real-profiles")
    directory.symlink_to("real-profiles", target_is_directory=True)
    with pytest.raises(ValueError):
        load_profile(config, "codex")


@pytest.mark.parametrize("mode", [0o644, 0o666, 0o700])
def test_permissive_profile_rejected(config, mode):
    (config / "profiles/codex.json").chmod(mode)
    with pytest.raises(ValueError):
        load_profile(config, "codex")


def test_permissive_directory_rejected(config):
    (config / "profiles").chmod(0o755)
    with pytest.raises(ValueError):
        load_profile(config, "codex")


def test_symlink_profile_rejected(config):
    path = config / "profiles/codex.json"
    path.rename(config / "profiles/real.json")
    path.symlink_to("real.json")
    with pytest.raises(ValueError):
        load_profile(config, "codex")


def test_identity_mismatch_rejected(config):
    path = config / "profiles/codex.json"
    path.write_text(path.read_text().replace("codex", "hermes"))
    with pytest.raises(ValueError):
        load_profile(config, "codex")


def test_wrong_owner_rejected(config, monkeypatch):
    monkeypatch.setattr(os, "getuid", lambda: -1)
    with pytest.raises(ValueError):
        load_profile(config, "codex")
