"""Exercise the MCP adapter through an actual stdio subprocess."""

import asyncio
import json
from pathlib import Path

import pytest
from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport

ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "data/synthetic/mcp-spike/context.json"


@pytest.fixture
def harness(tmp_path):
    script = tmp_path / "server.py"
    script.write_text(
        f"""\
import json
from pathlib import Path
from resume_core.logging_policy import configure_mcp_logging
configure_mcp_logging()
from resume_core.mcp_spike.contracts import ApplicationContext
from resume_core.mcp_spike.database import make_engine, metadata
from resume_core.mcp_spike.policy import Profile
from resume_core.mcp_spike.repository import Repository, TemporarilyUnavailable
from resume_core.mcp_spike.service import ContextService, ProgressService
from resume_mcp_server.server import create_server
context = ApplicationContext.model_validate(json.loads(Path({str(FIXTURE)!r}).read_text()))
mode_path = Path({str(tmp_path / "mode")!r})
mode = mode_path.read_text() if mode_path.exists() else "normal"
if mode == "oversize":
    context.approved_answers = ["x" * 17000]
def load_context(application_id):
    if mode == "missing":
        return None
    if mode == "unexpected":
        raise RuntimeError("private-sentinel")
    return context
engine = make_engine(Path({str(tmp_path / "mcp-spike.sqlite3")!r}))
metadata.create_all(engine)
profile = Profile(clientId="codex", applicationIds=["app-demo"], capabilities=["application_context:read", "application_progress:write"])
repository = Repository(engine)
if mode == "unavailable":
    def unavailable(*args):
        raise TemporarilyUnavailable("database-sentinel")
    repository.record = unavailable
create_server(profile, ContextService(load_context), ProgressService(repository)).run(transport="stdio", show_banner=False)
"""
    )
    return PythonStdioTransport(script_path=script, log_file=tmp_path / "stderr.log")


def run(coro):
    return asyncio.run(coro)


def text_payload(result):
    return json.loads(result.content[0].text)


def test_catalog_and_context(harness):
    async def scenario():
        async with Client(harness) as client:
            tools = await client.list_tools()
            assert {t.name for t in tools} == {
                "get_application_context",
                "report_application_progress",
            }
            context_tool = next(t for t in tools if t.name == "get_application_context")
            assert set(context_tool.inputSchema["properties"]) == {"applicationId"}
            response = await client.call_tool_mcp(
                "get_application_context", {"applicationId": "app-demo"}
            )
            assert not response.isError
            data = text_payload(response)
            assert data["schemaVersion"] == "m05.v1"
            assert data["data"] == json.loads(FIXTURE.read_text())
            assert data["policy"]["clientId"] == "codex"
            assert data["truncated"] is False

    run(scenario())


@pytest.mark.parametrize(
    "arguments",
    [
        {},
        {"applicationId": 12},
        {"applicationId": ""},
        {"applicationId": "a" * 129},
        {"applicationId": "á"},
        {"applicationId": "app-demo", "secret": "sentinel"},
        {"applicationId": "app-demo", "secret": "x" * 4097},
    ],
)
def test_invalid_arguments_are_safe(harness, arguments):
    async def scenario():
        async with Client(harness) as client:
            result = await client.call_tool_mcp("get_application_context", arguments)
            assert result.isError
            assert text_payload(result)["error"]["code"] == "SCHEMA_INVALID"
            assert "sentinel" not in result.content[0].text

    run(scenario())


def test_denied_application_and_progress_replay_conflict(harness):
    async def scenario():
        async with Client(harness) as client:
            denied = await client.call_tool_mcp(
                "get_application_context", {"applicationId": "other"}
            )
            assert denied.isError
            assert text_payload(denied)["error"]["code"] == "NOT_AUTHORIZED"
            args = {
                "applicationId": "app-demo",
                "executionId": "run-1",
                "idempotencyKey": "key-1",
                "event": "started",
            }
            first = await client.call_tool_mcp("report_application_progress", args)
            second = await client.call_tool_mcp("report_application_progress", args)
            assert not first.isError and not second.isError
            assert text_payload(first)["data"] == text_payload(second)["data"]
            assert text_payload(first)["data"]["confirmationState"] == "reported_by_agent"
            args["event"] = "blocked"
            conflict = await client.call_tool_mcp("report_application_progress", args)
            assert conflict.isError
            assert text_payload(conflict)["error"]["code"] == "CONFLICT"

    run(scenario())


@pytest.mark.parametrize(
    "extra", [{"clientId": "hermes"}, {"confirmationState": "confirmed"}, {"event": "submitted"}]
)
def test_progress_rejects_forbidden_fields_and_events(harness, extra):
    async def scenario():
        args = {
            "applicationId": "app-demo",
            "executionId": "run-1",
            "idempotencyKey": "key-1",
            "event": "started",
        } | extra
        async with Client(harness) as client:
            result = await client.call_tool_mcp("report_application_progress", args)
            assert result.isError
            assert text_payload(result)["error"]["code"] == "SCHEMA_INVALID"

    run(scenario())


@pytest.mark.parametrize(
    "mode,code",
    [
        ("missing", "CONTEXT_NOT_FOUND"),
        ("unexpected", "INTERNAL_ERROR"),
        ("oversize", "CONTEXT_TRUNCATED"),
    ],
)
def test_safe_service_errors(harness, tmp_path, mode, code):
    (tmp_path / "mode").write_text(mode)

    async def scenario():
        async with Client(harness) as client:
            result = await client.call_tool_mcp(
                "get_application_context", {"applicationId": "app-demo"}
            )
            assert result.isError
            assert text_payload(result)["error"]["code"] == code
            assert "private-sentinel" not in result.content[0].text

    run(scenario())
    assert "private-sentinel" not in (tmp_path / "stderr.log").read_text()


def test_persistence_failure_returns_temporary_error(harness, tmp_path):
    (tmp_path / "mode").write_text("unavailable")

    async def scenario():
        async with Client(harness) as client:
            result = await client.call_tool_mcp(
                "report_application_progress",
                {
                    "applicationId": "app-demo",
                    "executionId": "run-1",
                    "idempotencyKey": "key-1",
                    "event": "started",
                },
            )
            assert result.isError
            assert text_payload(result)["error"]["code"] == "TEMPORARILY_UNAVAILABLE"
            assert "database-sentinel" not in result.content[0].text

    run(scenario())
