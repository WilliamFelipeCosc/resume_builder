"""FND-18: allowlisted JSON for application and dependency logs."""

import io
import json
import logging
from datetime import datetime
from uuid import uuid4

import pytest
import structlog
from resume_core.logging_policy import configure_logging

SENTINEL = "SYNTHETIC_SECRET_SENTINEL"


@pytest.fixture
def output():
    loggers = [logging.getLogger()] + [
        value
        for value in logging.Logger.manager.loggerDict.values()
        if isinstance(value, logging.Logger)
    ]
    snapshots = [(value, value.handlers[:], value.level, value.propagate) for value in loggers]
    config = structlog.get_config()
    stream = io.StringIO()
    configure_logging(stream=stream)
    yield stream
    for logger, handlers, level, propagate in snapshots:
        logger.handlers = handlers
        logger.setLevel(level)
        logger.propagate = propagate
    structlog.configure(**config)
    structlog.contextvars.clear_contextvars()


def test_json_retains_only_valid_correlation_and_operation_fields(output):
    request_id, execution_id = uuid4(), uuid4()
    structlog.get_logger().info(
        "diagnostic_created",
        request_id=request_id,
        execution_id=str(execution_id),
        status="pending",
        attempt_count=0,
        cookie=SENTINEL,
        payload=SENTINEL,
    )
    event = json.loads(output.getvalue())
    assert event["event"] == "diagnostic_created"
    assert event["request_id"] == str(request_id)
    assert event["execution_id"] == str(execution_id)
    assert event["status"] == "pending"
    assert event["attempt_count"] == 0
    assert event["level"] == "info"
    assert datetime.fromisoformat(event["timestamp"]).utcoffset().total_seconds() == 0
    assert SENTINEL not in output.getvalue()
    assert set(event) == {
        "timestamp",
        "level",
        "event",
        "request_id",
        "execution_id",
        "status",
        "attempt_count",
    }


@pytest.mark.parametrize(
    "field",
    [
        "request_id",
        "execution_id",
        "status",
        "code",
        "method",
        "path",
        "status_code",
        "attempt_count",
    ],
)
def test_invalid_allowed_field_values_are_dropped(output, field):
    structlog.get_logger().warning("request_completed", **{field: SENTINEL})
    event = json.loads(output.getvalue())
    assert field not in event
    assert SENTINEL not in output.getvalue()


def test_unknown_event_and_raw_message_are_replaced(output):
    structlog.get_logger().warning(SENTINEL, ticket=SENTINEL)
    assert json.loads(output.getvalue())["event"] == "dependency_event"
    assert SENTINEL not in output.getvalue()


def test_standard_dependency_log_never_emits_raw_args_or_exception(output):
    try:
        raise RuntimeError(SENTINEL)
    except RuntimeError:
        logging.getLogger("dramatiq.worker").exception(
            "body=%s", SENTINEL, extra={"cookie": SENTINEL}
        )
    event = json.loads(output.getvalue())
    assert event["event"] == "dependency_event"
    assert event["level"] == "error"
    assert SENTINEL not in output.getvalue()
    assert "Traceback" not in output.getvalue()


def test_structlog_exception_never_emits_raw_stack_or_document(output):
    try:
        raise ValueError(SENTINEL)
    except ValueError:
        structlog.get_logger().exception("internal_error", code="internal_error", document=SENTINEL)
    event = json.loads(output.getvalue())
    assert event["event"] == "internal_error"
    assert event["code"] == "internal_error"
    assert SENTINEL not in output.getvalue()
    assert "Traceback" not in output.getvalue()


def test_context_correlation_survives_but_bound_credentials_do_not(output):
    request_id = uuid4()
    structlog.contextvars.bind_contextvars(request_id=str(request_id), cookie=SENTINEL)
    structlog.get_logger().info(
        "request_completed", method="POST", path="/api/diagnostics", status_code=202
    )
    event = json.loads(output.getvalue())
    assert event["request_id"] == str(request_id)
    assert event["method"] == "POST"
    assert event["path"] == "/api/diagnostics"
    assert event["status_code"] == 202
    assert SENTINEL not in output.getvalue()


def test_existing_dependency_handler_is_replaced_by_safe_pipeline(output):
    unsafe = io.StringIO()
    dependency = logging.getLogger("uvicorn.access")
    dependency.handlers = [logging.StreamHandler(unsafe)]
    dependency.propagate = False
    configure_logging(stream=output)
    dependency.info(SENTINEL)
    assert unsafe.getvalue() == ""
    assert json.loads(output.getvalue())["event"] == "dependency_event"
    assert SENTINEL not in output.getvalue()


def test_invalid_foreign_interpolation_never_exposes_logging_traceback(output):
    logging.getLogger("dramatiq.worker").error("unformatted %d " + SENTINEL, SENTINEL)
    assert json.loads(output.getvalue())["event"] == "dependency_event"
    assert SENTINEL not in output.getvalue()


def test_default_output_is_stderr_and_stdout_empty(output, monkeypatch):
    stderr, stdout = io.StringIO(), io.StringIO()
    monkeypatch.setattr("sys.stderr", stderr)
    monkeypatch.setattr("sys.stdout", stdout)
    configure_logging()
    structlog.get_logger().info("internal_error", code="internal_error")
    assert json.loads(stderr.getvalue())["event"] == "internal_error"
    assert stdout.getvalue() == ""
