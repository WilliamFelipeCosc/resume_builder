"""Process-wide allowlist: neither free-form messages nor exception text leave it."""

import logging
import sys
from datetime import UTC, datetime
from typing import TextIO
from uuid import UUID

import structlog

EVENTS = frozenset(
    {
        "request_completed",
        "diagnostic_created",
        "diagnostic_queued",
        "diagnostic_claimed",
        "diagnostic_succeeded",
        "diagnostic_failed",
        "delivery_failed",
        "reconciliation_completed",
        "session_started",
        "bootstrap_rejected",
        "internal_error",
        "dependency_event",
        "mcp_server_started",
        "mcp_request_completed",
        "mcp_request_failed",
    }
)
CODES = frozenset(
    {"queue_unavailable", "deadline_exceeded", "attempts_exhausted", "internal_error"}
)
PATHS = frozenset(
    {"/api/health", "/api/diagnostics", "/api/diagnostics/latest", "/api/session/bootstrap"}
)


def sanitize_event(_logger, method, event):
    candidate = event.get("event")
    safe = {
        "timestamp": datetime.now(UTC).isoformat(),
        "level": method if method in {"debug", "info", "warning", "error", "critical"} else "info",
        "event": candidate
        if isinstance(candidate, str) and candidate in EVENTS
        else "dependency_event",
    }
    for key in ("request_id", "execution_id"):
        value = event.get(key)
        if isinstance(value, (str, UUID)):
            try:
                safe[key] = str(UUID(str(value)))
            except ValueError:
                pass
    for key, choices in (
        ("status", {"pending", "queued", "running", "succeeded", "failed"}),
        ("code", CODES),
        ("method", {"GET", "POST"}),
        ("path", PATHS),
    ):
        value = event.get(key)
        if isinstance(value, str) and value in choices:
            safe[key] = value
    for key, minimum, maximum in (("status_code", 100, 599), ("attempt_count", 0, 3)):
        value = event.get(key)
        if type(value) is int and minimum <= value <= maximum:
            safe[key] = value
    return safe


def configure_logging(*, stream: TextIO | None = None) -> None:
    """Call at process startup; dependencies must not replace handlers afterward."""
    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[sanitize_event, structlog.processors.JSONRenderer()],
        foreign_pre_chain=[structlog.contextvars.merge_contextvars],
        use_get_message=False,
    )
    handler = logging.StreamHandler(stream if stream is not None else sys.stderr)
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)
    logging.raiseExceptions = False
    for logger in tuple(logging.Logger.manager.loggerDict.values()):
        if isinstance(logger, logging.Logger):
            logger.handlers = []
            logger.propagate = True
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=False,
    )


def configure_mcp_logging(*, stream: TextIO | None = None) -> None:
    """Load FastMCP's handlers first, then replace them with the allowlist."""
    import fastmcp  # noqa: F401

    configure_logging(stream=stream)
