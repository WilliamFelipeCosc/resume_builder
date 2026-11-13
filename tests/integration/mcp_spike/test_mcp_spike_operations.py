"""Local lifecycle commands operate only on the isolated synthetic environment."""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest
from fastmcp import Client
from fastmcp.client.transports import StdioTransport

LAUNCHER = Path(__file__).resolve().parents[3] / "tools/mcp-spike-launch"


@pytest.fixture
def env(tmp_path):
    return os.environ | {
        "XDG_DATA_HOME": str(tmp_path / "data"),
        "XDG_CONFIG_HOME": str(tmp_path / "config"),
        "XDG_CACHE_HOME": str(tmp_path / "cache"),
        "XDG_STATE_HOME": str(tmp_path / "state"),
    }


def cli(env, *args):
    return subprocess.run(
        [sys.executable, "-m", "resume_mcp_server", *args],
        env=env,
        text=True,
        capture_output=True,
        timeout=20,
    )


def paths(env):
    suffix = Path("resume-builder/mcp-spike")
    return Path(env["XDG_CONFIG_HOME"]) / suffix, Path(env["XDG_DATA_HOME"]) / suffix


def test_init_creates_private_synthetic_environment_and_is_idempotent(env):
    assert cli(env, "init").returncode == 0
    config, data = paths(env)
    assert (config.stat().st_mode & 0o777) == 0o700
    assert (data.stat().st_mode & 0o777) == 0o700
    for name in ("hermes", "codex"):
        profile = config / "profiles" / f"{name}.json"
        assert profile.stat().st_mode & 0o777 == 0o600
        assert json.loads(profile.read_text())["clientId"] == name
    assert (data / "mcp-spike.sqlite3").is_file()
    assert cli(env, "init").returncode == 0


@pytest.mark.parametrize(
    "command", [("serve", "--profile", "codex"), ("reports", "--profile", "codex")]
)
def test_uninitialized_commands_fail_without_creating_state(env, command):
    result = cli(env, *command)
    assert result.returncode != 0
    assert not paths(env)[1].exists()
    assert result.stdout == ""


def test_removed_profile_denies_restart(env):
    assert cli(env, "init").returncode == 0
    (paths(env)[0] / "profiles/codex.json").unlink()
    result = cli(env, "serve", "--profile", "codex")
    assert result.returncode != 0
    assert result.stdout == ""


def test_permissive_data_directory_denies_serve(env):
    assert cli(env, "init").returncode == 0
    paths(env)[1].chmod(0o755)
    result = cli(env, "serve", "--profile", "codex")
    assert result.returncode != 0
    assert result.stdout == ""


def test_serve_refuses_obsolete_schema_without_migration(env):
    import sqlite3

    assert cli(env, "init").returncode == 0
    db = paths(env)[1] / "mcp-spike.sqlite3"
    with sqlite3.connect(db) as connection:
        connection.execute("DELETE FROM alembic_version")
    assert cli(env, "serve", "--profile", "codex").returncode != 0
    with sqlite3.connect(db) as connection:
        assert connection.execute("SELECT COUNT(*) FROM alembic_version").fetchone()[0] == 0


@pytest.mark.parametrize(
    "args",
    [
        ("serve",),
        ("serve", "--profile", "unknown"),
        ("reports", "--profile", "codex", "--sql", "select 1"),
        ("init", "--path", "/tmp/other"),
    ],
)
def test_rejects_unsanctioned_cli_arguments(env, args):
    assert cli(env, *args).returncode != 0


def test_profile_and_database_symlinks_are_rejected(env, tmp_path):
    assert cli(env, "init").returncode == 0
    config, data = paths(env)
    profile = config / "profiles/codex.json"
    profile.unlink()
    profile.symlink_to(tmp_path / "nonexistent")
    assert cli(env, "serve", "--profile", "codex").returncode != 0
    db = data / "mcp-spike.sqlite3"
    db.unlink()
    db.symlink_to(tmp_path / "nonexistent")
    assert cli(env, "init").returncode != 0


def test_reports_filter_profile_and_restart_preserves_receipt(env):
    import asyncio

    assert cli(env, "init").returncode == 0

    async def call():
        transport = StdioTransport(
            command=sys.executable,
            args=["-m", "resume_mcp_server", "serve", "--profile", "codex"],
            env=env,
        )
        async with Client(transport) as client:
            result = await client.call_tool_mcp(
                "report_application_progress",
                {
                    "applicationId": "app-demo",
                    "executionId": "run",
                    "idempotencyKey": "key",
                    "event": "started",
                },
            )
            assert not result.is_error
            return json.loads(result.content[0].text)["data"]["receiptId"]

    assert asyncio.run(call()) == asyncio.run(call())
    codex = json.loads(cli(env, "reports", "--profile", "codex").stdout)
    hermes = json.loads(cli(env, "reports", "--profile", "hermes").stdout)
    assert len(codex) == 1
    assert codex[0]["event"] == "started"
    assert hermes == []


def test_server_startup_and_denied_query_do_not_read_fixture(env, monkeypatch):
    from unittest.mock import Mock

    from resume_core.mcp_spike.contracts import ContextQuery
    from resume_core.paths import resolve_paths
    from resume_core.service import PermissionDenied
    from resume_mcp_server import __main__ as lifecycle
    from resume_mcp_server import server

    assert cli(env, "init").returncode == 0
    config, _ = paths(env)
    profile_path = config / "profiles/codex.json"
    profile = json.loads(profile_path.read_text())
    profile["capabilities"] = []
    profile_path.write_text(json.dumps(profile))
    fixture = Mock()
    monkeypatch.setattr(lifecycle, "FIXTURE", fixture)
    monkeypatch.setattr("resume_core.logging_policy.configure_mcp_logging", lambda: None)

    def create(principal, contexts, progress):
        fixture.read_text.assert_not_called()
        with pytest.raises(PermissionDenied):
            contexts.get(principal, ContextQuery(applicationId="app-demo"))
        fixture.read_text.assert_not_called()
        return Mock()

    monkeypatch.setattr(server, "create_server", create)
    lifecycle._serve(resolve_paths("mcp-spike", env), "codex")
    fixture.read_text.assert_not_called()


def test_malformed_json_frame_is_sanitized_and_does_not_block_next_frame(env):
    assert cli(env, "init").returncode == 0
    initialize = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-11-25",
            "capabilities": {},
            "clientInfo": {"name": "synthetic-test", "version": "1"},
        },
    }
    result = subprocess.run(
        [sys.executable, "-m", "resume_mcp_server", "serve", "--profile", "codex"],
        env=env,
        input="{malformed-frame-sentinel\n" + json.dumps(initialize) + "\n",
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert "malformed-frame-sentinel" not in result.stdout
    assert "malformed-frame-sentinel" not in result.stderr
    responses = [json.loads(line) for line in result.stdout.splitlines()]
    assert all(response["jsonrpc"] == "2.0" for response in responses)
    assert any(response.get("id") == 1 and "result" in response for response in responses)


@pytest.mark.parametrize("size", [4097, 65536])
def test_large_valid_protocol_frame_is_not_a_domain_input_limit(env, size):
    assert cli(env, "init").returncode == 0
    initialize = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "padding": "x" * size,
        "params": {
            "protocolVersion": "2025-11-25",
            "capabilities": {},
            "clientInfo": {"name": "synthetic-test", "version": "1"},
        },
    }
    result = subprocess.run(
        [sys.executable, "-m", "resume_mcp_server", "serve", "--profile", "codex"],
        env=env,
        input=json.dumps(initialize) + "\n",
        capture_output=True,
        text=True,
        timeout=20,
    )
    responses = [json.loads(line) for line in result.stdout.splitlines()]
    assert any(response.get("id") == 1 and "result" in response for response in responses)


@pytest.mark.parametrize("profile", ["hermes", "codex"])
def test_launcher_limits_server_environment(env, profile):
    assert cli(env, "init").returncode == 0
    parent_env = env | {"M05_FAKE_SECRET_SENTINEL": "synthetic-secret"}
    process = subprocess.Popen(
        [str(LAUNCHER), profile],
        env=parent_env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            assert process.poll() is None
            cmdline = Path(f"/proc/{process.pid}/cmdline").read_bytes().split(b"\0")
            if b"resume_mcp_server" in cmdline:
                break
            time.sleep(0.01)
        else:
            pytest.fail("MCP server did not start")
        environment = Path(f"/proc/{process.pid}/environ").read_bytes().split(b"\0")
        keys = {item.split(b"=", 1)[0].decode() for item in environment if item}
        assert keys == {
            "HOME",
            "XDG_DATA_HOME",
            "XDG_CONFIG_HOME",
            "XDG_CACHE_HOME",
            "XDG_STATE_HOME",
            "PATH",
            "LANG",
        }
        assert "M05_FAKE_SECRET_SENTINEL" not in keys
    finally:
        process.terminate()
        process.communicate(timeout=10)


def test_launcher_rejects_unrecognized_profile(env):
    result = subprocess.run([str(LAUNCHER), "other"], env=env, capture_output=True, text=True)
    assert result.returncode != 0
    assert result.stdout == ""
