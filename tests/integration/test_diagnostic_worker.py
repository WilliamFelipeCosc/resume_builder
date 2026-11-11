"""FND-02/09/10/11/12/18: fixture processing, fencing and a real Worker process."""

import io
import json
import subprocess
import sys
import time
from datetime import UTC, datetime
from uuid import uuid4

from resume_core.broker import RedisPublisher
from resume_core.contracts import DiagnosticResult
from resume_core.logging_policy import configure_logging
from resume_worker.diagnostic import create_actor, process_diagnostic


def intention(repo):
    return repo.create(uuid4(), uuid4()).execution


def wait_until(predicate, timeout=8):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.02)
    raise AssertionError("Worker outcome was not observed")


def test_real_separate_worker_process_fixed_result_and_duplicate_delivery(
    repository, redis_broker, isolated_redis
):
    repo, _ = repository
    repo.clock = lambda: datetime.now(UTC)
    execution = intention(repo)
    database = str(repo.engine.url.database)
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "resume_worker",
            "--database",
            database,
            "--redis-url",
            isolated_redis.url,
            "--namespace",
            redis_broker.namespace,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        publisher = RedisPublisher(redis_broker)
        publisher.publish(execution)
        wait_until(lambda: repo.get(execution.id).status == "succeeded")
        completed = repo.get(execution.id)
        assert completed.id == execution.id
        assert completed.request_id == execution.request_id
        assert completed.result == DiagnosticResult()
        assert completed.error is completed.delivery_warning is None
        assert completed.attempt_count == 1
        publisher.publish(execution)
        publisher.publish(execution)
        redis_broker.join("diagnostics", timeout=3000)
        assert repo.get(execution.id) == completed
    finally:
        process.terminate()
        stdout, stderr = process.communicate(timeout=8)
    assert process.returncode == 0
    assert stdout == ""
    events = [json.loads(line) for line in stderr.splitlines()]
    claimed = [event for event in events if event["event"] == "diagnostic_claimed"]
    assert len(claimed) == 1
    assert claimed[0]["request_id"] == str(execution.request_id)
    assert claimed[0]["execution_id"] == str(execution.id)
    assert claimed[0]["attempt_count"] == 1
    assert any(event["event"] == "diagnostic_succeeded" for event in events)


def test_worker_never_processes_without_claim(repository):
    repo, _ = repository
    execution = intention(repo)
    lease = repo.claim(execution.id)

    def poison():
        raise AssertionError("fixture must not run")

    assert not process_diagnostic(repo, execution.id, execution.request_id, fixture=poison)
    assert repo.get(execution.id) == lease.execution


def test_attempt_exact_30_seconds_cannot_commit(repository):
    repo, clock = repository
    execution = intention(repo)

    def slow():
        clock.advance(30)
        return DiagnosticResult()

    assert not process_diagnostic(repo, execution.id, execution.request_id, fixture=slow)
    assert repo.get(execution.id).status == "running"
    assert repo.get(execution.id).result is None
    assert repo.reconcile() == 1
    assert repo.get(execution.id).status == "pending"
    assert repo.get(execution.id).attempt_count == 1


def test_worker_cannot_start_past_total_deadline(repository):
    repo, clock = repository
    execution = intention(repo)
    clock.advance(120)
    assert not process_diagnostic(repo, execution.id, execution.request_id)
    assert repo.get(execution.id).attempt_count == 0
    repo.reconcile()
    assert repo.get(execution.id).error.code == "deadline_exceeded"


def test_third_failed_fixture_is_terminal_without_broker_retry(repository):
    repo, _ = repository
    execution = intention(repo)

    def broken():
        raise RuntimeError("PRIVATE_SENTINEL_WORKER")

    for count in range(1, 4):
        assert not process_diagnostic(repo, execution.id, execution.request_id, fixture=broken)
        assert repo.get(execution.id).attempt_count == count
    failed = repo.get(execution.id)
    assert failed.status == "failed"
    assert failed.error.code == "attempts_exhausted"
    assert failed.result is failed.delivery_warning is None
    assert not process_diagnostic(repo, execution.id, execution.request_id)
    assert repo.get(execution.id) == failed


def test_wrong_correlation_never_claims(repository):
    repo, _ = repository
    execution = intention(repo)
    assert not process_diagnostic(repo, execution.id, uuid4())
    assert not process_diagnostic(repo, "invalid", execution.request_id)
    assert repo.get(execution.id) == execution


def test_post_commit_failure_and_replay_do_not_duplicate(repository):
    repo, _ = repository
    execution = intention(repo)

    class AfterCommit:
        def __getattr__(self, name):
            return getattr(repo, name)

        def complete(self, execution_id, token):
            assert repo.complete(execution_id, token)
            raise RuntimeError("PRIVATE_SENTINEL_AFTER_COMMIT")

    assert not process_diagnostic(AfterCommit(), execution.id, execution.request_id)
    terminal = repo.get(execution.id)
    assert terminal.status == "succeeded"
    assert terminal.attempt_count == 1
    assert terminal.result == DiagnosticResult()
    assert not process_diagnostic(repo, execution.id, execution.request_id)
    assert repo.get(execution.id) == terminal


def test_worker_error_logs_are_json_and_sanitized(repository):
    repo, _ = repository
    output = io.StringIO()
    configure_logging(stream=output)
    execution = intention(repo)

    def broken():
        raise RuntimeError("PRIVATE_SENTINEL_WORKER")

    assert not process_diagnostic(repo, execution.id, execution.request_id, fixture=broken)
    records = [json.loads(line) for line in output.getvalue().splitlines()]
    failure = [event for event in records if event["event"] == "diagnostic_failed"][0]
    assert failure["code"] == "internal_error"
    assert failure["request_id"] == str(execution.request_id)
    assert failure["execution_id"] == str(execution.id)
    assert "PRIVATE_SENTINEL" not in output.getvalue()
    assert "Traceback" not in output.getvalue()
    assert repo.get(execution.id).status == "pending"


def test_actor_has_no_automatic_retry_and_bounded_fixture(repository, redis_broker):
    repo, _ = repository
    actor = create_actor(repo, redis_broker)
    assert actor.options["max_retries"] == 0
    assert actor.options["time_limit"] == 30_000


def test_worker_startup_failure_is_sanitized():
    completed = subprocess.run(
        [sys.executable, "-m", "resume_worker", "--database", "PRIVATE_SENTINEL_RELATIVE"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 1
    assert completed.stdout == ""
    assert "PRIVATE_SENTINEL" not in completed.stderr
    assert "Traceback" not in completed.stderr
    assert json.loads(completed.stderr)["code"] == "internal_error"
