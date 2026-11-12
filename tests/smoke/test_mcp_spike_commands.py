"""The just entry points map to scoped local commands without live providers."""

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def just(*args):
    result = subprocess.run(["just", *args], cwd=ROOT, text=True, capture_output=True, check=True)
    return result.stdout + result.stderr


def test_spike_commands_are_listed():
    output = just("--list")
    for name in (
        "mcp-spike-init",
        "mcp-spike-serve",
        "mcp-spike-form",
        "mcp-spike-reports",
        "check-mcp-spike",
    ):
        assert name in output


@pytest.mark.parametrize(
    "recipe,arguments,expected",
    [
        ("mcp-spike-init", [], "resume_mcp_server init"),
        ("mcp-spike-serve", ["codex"], "resume_mcp_server serve --profile 'codex'"),
        ("mcp-spike-form", [], "resume_mcp_server.form_server"),
        ("mcp-spike-reports", ["hermes"], "resume_mcp_server reports --profile 'hermes'"),
    ],
)
def test_dry_runs_call_scoped_installed_commands(recipe, arguments, expected):
    output = just("--dry-run", recipe, *arguments)
    assert expected in output
    assert "--no-sync" in output
    assert "uv sync" not in output


def test_check_runs_deterministic_tests_only():
    output = just("--dry-run", "check-mcp-spike")
    assert "pytest" in output
    assert "tests/unit/mcp_spike" in output
    assert "tests/integration/mcp_spike" in output
    assert "resume_mcp_server serve" not in output
    assert "hermes" not in output
