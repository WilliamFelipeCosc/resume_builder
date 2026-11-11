"""One fixed synthetic fixture, guarded by the canonical SQLite lease."""

from uuid import UUID

import dramatiq
import structlog
from resume_core.broker import ACTOR, QUEUE
from resume_core.contracts import DiagnosticResult


def run_fixture():
    return DiagnosticResult()


def process_diagnostic(repository, execution_id, request_id, *, fixture=run_fixture) -> bool:
    try:
        execution_id, request_id = UUID(str(execution_id)), UUID(str(request_id))
    except ValueError:
        return False
    existing = repository.get(execution_id)
    if existing is None or existing.request_id != request_id:
        return False
    lease = repository.claim(execution_id)
    if lease is None:
        return False
    metadata = dict(
        execution_id=execution_id,
        request_id=existing.request_id,
        attempt_count=lease.execution.attempt_count,
    )
    logger = structlog.get_logger()
    logger.info("diagnostic_claimed", **metadata)
    try:
        if fixture() != DiagnosticResult():
            raise ValueError("Unexpected diagnostic fixture result")
        completed = repository.complete(execution_id, lease.token)
    except Exception:
        repository.fail_attempt(execution_id, lease.token)
        logger.error("diagnostic_failed", code="internal_error", **metadata)
        return False
    if completed:
        logger.info("diagnostic_succeeded", **metadata)
    return completed


def create_actor(repository, broker):
    @dramatiq.actor(
        broker=broker, actor_name=ACTOR, queue_name=QUEUE, max_retries=0, time_limit=30_000
    )
    def run_diagnostic(execution_id: str, request_id: str):
        process_diagnostic(repository, execution_id, request_id)

    return run_diagnostic
