"""FND-19/21/22/23: explicit local commands use only their selected test environment."""

import json
import os
import sqlite3
import subprocess
import sys


def invoke(tmp_path, *arguments, environment="test"):
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "resume_api",
            "--environment",
            environment,
            "--test-root",
            str(tmp_path / "isolated"),
            *arguments,
        ],
        env={**os.environ, "XDG_RUNTIME_DIR": str(tmp_path)},
        capture_output=True,
        text=True,
        check=False,
    )


def test_migrate_creates_only_isolated_schema_and_is_repeatable(tmp_path):
    for _ in range(2):
        result = invoke(tmp_path, "migrate")
        assert result.returncode == 0, result.stderr
        assert result.stdout == ""
    root = tmp_path / "isolated"
    database = root / "data/diagnostics.sqlite3"
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT count(*) FROM diagnostic_runs").fetchone() == (0,)
        assert connection.execute("SELECT version_num FROM alembic_version").fetchone() == (
            "0003_kb_entities",
        )
    assert {path.name for path in root.iterdir()} == {"data", "config", "cache", "state"}
    assert not (tmp_path / "resume-builder").exists()


def test_serve_requires_explicit_migration_without_creating_a_database(tmp_path):
    result = invoke(tmp_path, "serve")
    assert result.returncode == 1
    assert result.stdout == ""
    assert json.loads(result.stderr)["code"] == "internal_error"
    assert not (tmp_path / "isolated").exists()


def test_unsafe_environment_rejected_without_echo_or_mutation(tmp_path):
    result = invoke(tmp_path, "migrate", environment="../PRIVATE_SENTINEL")
    assert result.returncode == 1
    assert "PRIVATE_SENTINEL" not in result.stdout + result.stderr
    assert json.loads(result.stderr)["code"] == "internal_error"
    assert list(tmp_path.iterdir()) == []


def test_cli_does_not_allow_nonloopback_host_override(tmp_path):
    result = invoke(tmp_path, "serve", "--host", "0.0.0.0")
    assert result.returncode != 0
    assert not (tmp_path / "isolated").exists()


def test_just_commands_do_not_implicitly_start_redis_or_install_system_packages():
    result = subprocess.run(["just", "--list"], capture_output=True, text=True, check=True)
    for name in ["migrate", "api", "worker", "open", "redis-up", "redis-down", "check"]:
        assert name in result.stdout
    dry_run = subprocess.run(
        ["just", "--dry-run", "api"], capture_output=True, text=True, check=True
    )
    assert "resume_api serve" in dry_run.stderr
    assert "docker" not in dry_run.stderr
