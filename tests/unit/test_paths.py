"""FND-22/23: environment isolation, no private data, no automatic services."""

from pathlib import Path

import pytest
from resume_core.paths import resolve_paths


def test_xdg_paths_are_namespaced_without_creation(tmp_path):
    env = {
        key: str(tmp_path / key)
        for key in ["XDG_DATA_HOME", "XDG_CONFIG_HOME", "XDG_CACHE_HOME", "XDG_STATE_HOME"]
    }
    paths = resolve_paths("development", env)
    assert paths.data == tmp_path / "XDG_DATA_HOME/resume-builder/development"
    assert paths.config == tmp_path / "XDG_CONFIG_HOME/resume-builder/development"
    assert paths.cache == tmp_path / "XDG_CACHE_HOME/resume-builder/development"
    assert paths.state == tmp_path / "XDG_STATE_HOME/resume-builder/development"
    assert list(tmp_path.iterdir()) == []


def test_xdg_defaults_use_home(tmp_path):
    paths = resolve_paths("development", {"HOME": str(tmp_path)})
    assert paths.data == tmp_path / ".local/share/resume-builder/development"
    assert paths.config == tmp_path / ".config/resume-builder/development"
    assert paths.cache == tmp_path / ".cache/resume-builder/development"
    assert paths.state == tmp_path / ".local/state/resume-builder/development"


@pytest.mark.parametrize(
    "environment", ["", "../development", "/tmp", "TEST", "test/../../development"]
)
def test_invalid_environment_is_rejected(environment, tmp_path):
    with pytest.raises(ValueError, match="environment"):
        resolve_paths(environment, {"HOME": str(tmp_path)})


def test_test_environment_requires_explicit_temporary_root(tmp_path):
    with pytest.raises(ValueError, match="test_root"):
        resolve_paths("test", {"XDG_DATA_HOME": str(tmp_path)})


def test_test_ignores_local_xdg_and_home(tmp_path):
    paths = resolve_paths(
        "test",
        {"HOME": "/do-not-read-private", "XDG_DATA_HOME": "/do-not-read-private"},
        test_root=tmp_path,
    )
    assert paths.data == tmp_path / "data"
    assert paths.config == tmp_path / "config"
    assert paths.cache == tmp_path / "cache"
    assert paths.state == tmp_path / "state"


def test_non_test_environment_rejects_test_root(tmp_path):
    with pytest.raises(ValueError, match="test_root"):
        resolve_paths("development", {"HOME": str(tmp_path)}, test_root=tmp_path)


def test_test_root_outside_temp_is_rejected():
    with pytest.raises(ValueError, match="temporary"):
        resolve_paths("test", {}, test_root=Path.home() / "resume-tests")


@pytest.mark.parametrize(
    "key", ["HOME", "XDG_DATA_HOME", "XDG_CONFIG_HOME", "XDG_CACHE_HOME", "XDG_STATE_HOME"]
)
def test_relative_configuration_is_rejected(key, tmp_path):
    with pytest.raises(ValueError, match="absolute"):
        resolve_paths("development", {"HOME": str(tmp_path), key: "relative"})


def test_symlink_is_rejected(tmp_path):
    target = tmp_path / "target"
    target.mkdir()
    link = tmp_path / "link"
    link.symlink_to(target)
    with pytest.raises(ValueError, match="symlink"):
        resolve_paths("development", {"HOME": str(tmp_path), "XDG_DATA_HOME": str(link)})


def test_created_directories_are_private(tmp_path):
    paths = resolve_paths("test", {}, test_root=tmp_path)
    paths.create()
    for path in [paths.data, paths.config, paths.cache, paths.state]:
        assert path.is_dir()
        assert path.stat().st_mode & 0o777 == 0o700


def test_existing_insecure_directory_is_rejected_without_repair(tmp_path):
    paths = resolve_paths("test", {}, test_root=tmp_path)
    paths.data.mkdir(mode=0o755)
    with pytest.raises(ValueError, match="private"):
        paths.create()
    assert paths.data.stat().st_mode & 0o777 == 0o755
