"""The MCP process shares the restrictive logging policy with M0."""

import json
import logging
from io import StringIO

import pytest
import structlog
from resume_core.logging_policy import configure_logging


@pytest.mark.parametrize(
    "event", ["mcp_server_started", "mcp_request_completed", "mcp_request_failed"]
)
def test_mcp_events_are_identifiable_without_sensitive_fields(event):
    output = StringIO()
    configure_logging(stream=output)
    structlog.get_logger().info(event, payload="secret-sentinel", path="/private/secret")
    record = json.loads(output.getvalue())
    assert record["event"] == event
    assert "secret-sentinel" not in output.getvalue()
    assert "/private/secret" not in output.getvalue()


def test_unknown_event_and_exception_are_sanitized():
    output = StringIO()
    configure_logging(stream=output)
    try:
        raise ValueError("exception-sentinel")
    except ValueError:
        logging.getLogger("mcp").exception("message-sentinel")
    record = json.loads(output.getvalue())
    assert record["event"] == "dependency_event"
    assert "sentinel" not in output.getvalue()
