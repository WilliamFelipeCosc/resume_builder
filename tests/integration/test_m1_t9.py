"""Operational logs contain no private career content, even from dependencies."""

import io
import json
import logging

import structlog
from resume_core.logging_policy import configure_logging


def test_application_and_dependency_logs_reject_private_values():
    output = io.StringIO()
    configure_logging(stream=output)
    sentinel = "CONTACT_SENTINEL EXCERPT_SENTINEL FILENAME_SENTINEL EXCEPTION_SENTINEL"
    structlog.get_logger().info(
        "career_read",
        path="/api/career/{kind}/{id}",
        code="stale_revision",
        contact=sentinel,
        excerpt=sentinel,
        filename=sentinel,
        exception=sentinel,
    )
    logging.getLogger("dependency").error(sentinel, exc_info=ValueError(sentinel))
    structlog.get_logger().info("request_completed", path="/api/career/SECRET?filename=PRIVATE")
    lines = [json.loads(line) for line in output.getvalue().splitlines()]
    assert lines[0]["event"] == "career_read"
    assert lines[0]["path"] == "/api/career/{kind}/{id}"
    assert lines[0]["code"] == "stale_revision"
    assert lines[1]["event"] == "dependency_event"
    assert "path" not in lines[2]
    for part in sentinel.split():
        assert part not in output.getvalue()
    assert "SECRET" not in output.getvalue() and "PRIVATE" not in output.getvalue()
