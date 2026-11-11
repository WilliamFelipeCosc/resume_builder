"""FND-07..12/21/22: faults exercised against real Redis and real Worker processes."""

import asyncio
import json
import signal
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

from resume_api.delivery import DiagnosticReconciler
from resume_core.broker import QUEUE, RedisPublisher
from resume_core.contracts import DiagnosticResult


def wait_for(predicate, timeout=10):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.02)
    raise AssertionError("Expected resilience outcome was not observed")


@contextmanager
def controlled_worker(repo, broker, redis, clock, tmp_path, *, mode="fixed", label="worker"):
    directory = tmp_path / label
    directory.mkdir()
    clock_file = tmp_path / "clock.json"
    clock_file.write_text(json.dumps(clock().isoformat()))
    process = subprocess.Popen(
        [
            sys.executable,
            str(Path(__file__).with_name("controlled_worker.py")),
            str(repo.engine.url.database),
            redis.url,
            broker.namespace,
            str(clock_file),
            str(directory),
            mode,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        yield process, directory, clock_file
    finally:
        if process.poll() is None:
            process.send_signal(signal.SIGCONT)
            (directory / "release").touch()
            process.terminate()
        stdout, stderr = process.communicate(timeout=10)
        assert stdout == ""
        assert "PRIVATE_SENTINEL" not in stderr
        assert "Traceback" not in stderr


def advance(clock, clock_file, seconds):
    clock.advance(seconds)
    temporary = clock_file.with_suffix(".next")
    temporary.write_text(json.dumps(clock().isoformat()))
    temporary.replace(clock_file)


def run_tick(repo, broker):
    asyncio.run(DiagnosticReconciler(repo, RedisPublisher(broker)).tick())


def create(repo):
    return repo.create(uuid4(), uuid4()).execution


def assert_success(repo, execution, attempts):
    wait_for(lambda: repo.get(execution.id).status == "succeeded")
    result = repo.get(execution.id)
    assert result.id == execution.id and result.request_id == execution.request_id
    assert result.idempotency_key == execution.idempotency_key
    assert result.attempt_count == attempts
    assert result.result == DiagnosticResult()
    assert result.error is result.delivery_warning is None
    return result


def test_real_worker_killed_during_claim_recovers_same_execution(
    repository, redis_broker, isolated_redis, tmp_path
):
    repo, clock = repository
    execution = create(repo)
    with controlled_worker(
        repo, redis_broker, isolated_redis, clock, tmp_path, mode="block", label="old"
    ) as (old, control, clock_file):
        run_tick(repo, redis_broker)
        wait_for(lambda: (control / "claimed").exists())
        assert repo.get(execution.id).status == "running"
        assert repo.get(execution.id).attempt_count == 1
        old.kill()
        old.wait(timeout=5)
        assert old.returncode < 0
        advance(clock, clock_file, 30)
        run_tick(repo, redis_broker)
        with controlled_worker(
            repo, redis_broker, isolated_redis, clock, tmp_path, label="restarted"
        ):
            completed = assert_success(repo, execution, 2)
            RedisPublisher(redis_broker).publish(execution)
            time.sleep(0.15)
            assert repo.get(execution.id) == completed


def test_old_real_worker_cannot_commit_after_new_owner_completes(
    repository, redis_broker, isolated_redis, tmp_path
):
    repo, clock = repository
    execution = create(repo)
    with controlled_worker(
        repo, redis_broker, isolated_redis, clock, tmp_path, mode="block", label="old"
    ) as (old_process, old, clock_file):
        run_tick(repo, redis_broker)
        wait_for(lambda: (old / "claimed").exists())
        # Freeze all old threads so its consumer cannot prefetch the recovery message.
        old_process.send_signal(signal.SIGSTOP)
        advance(clock, clock_file, 30)
        run_tick(repo, redis_broker)
        with controlled_worker(repo, redis_broker, isolated_redis, clock, tmp_path, label="new"):
            terminal = assert_success(repo, execution, 2)
            (old / "release").touch()
            old_process.send_signal(signal.SIGCONT)
            wait_for(lambda: (old / "outcome").exists())
            assert json.loads((old / "outcome").read_text()) is False
            assert repo.get(execution.id) == terminal


def test_redis_outage_recovers_to_actual_worker_without_new_intention(
    repository, redis_broker, isolated_redis, tmp_path
):
    repo, clock = repository
    execution = create(repo)
    isolated_redis.stop()
    try:
        run_tick(repo, redis_broker)
        waiting = repo.get(execution.id)
        assert waiting.status == "pending" and waiting.attempt_count == 0
        assert waiting.delivery_warning.code == "queue_unavailable"
        assert waiting.error is None
    finally:
        isolated_redis.start()
    clock.advance(1)
    run_tick(repo, redis_broker)
    with controlled_worker(repo, redis_broker, isolated_redis, clock, tmp_path):
        assert_success(repo, execution, 1)


def test_acknowledged_queue_loss_recovers_to_actual_worker(
    repository, redis_broker, isolated_redis, tmp_path
):
    repo, clock = repository
    execution = create(repo)
    run_tick(repo, redis_broker)
    assert repo.get(execution.id).status == "queued"
    redis_broker.flush(QUEUE)
    assert redis_broker.do_qsize(QUEUE) == 0
    clock.advance(1)
    run_tick(repo, redis_broker)
    with controlled_worker(repo, redis_broker, isolated_redis, clock, tmp_path):
        assert_success(repo, execution, 1)


def test_total_deadline_fences_real_blocked_worker_and_late_messages(
    repository, redis_broker, isolated_redis, tmp_path
):
    repo, clock = repository
    execution = create(repo)
    with controlled_worker(repo, redis_broker, isolated_redis, clock, tmp_path, mode="block") as (
        _,
        control,
        clock_file,
    ):
        run_tick(repo, redis_broker)
        wait_for(lambda: (control / "claimed").exists())
        advance(clock, clock_file, 120)
        run_tick(repo, redis_broker)
        failed = repo.get(execution.id)
        assert failed.status == "failed" and failed.error.code == "deadline_exceeded"
        assert failed.attempt_count == 1 and failed.result is failed.delivery_warning is None
        (control / "release").touch()
        wait_for(lambda: (control / "outcome").exists())
        assert json.loads((control / "outcome").read_text()) is False
        RedisPublisher(redis_broker).publish(execution)
        time.sleep(0.15)
        assert repo.get(execution.id) == failed


def test_three_actual_failed_attempts_exhaust_budget_without_automatic_retry(
    repository, redis_broker, isolated_redis, tmp_path
):
    repo, clock = repository
    execution = create(repo)
    with controlled_worker(repo, redis_broker, isolated_redis, clock, tmp_path, mode="fail") as (
        _,
        control,
        clock_file,
    ):
        for count in range(1, 4):
            run_tick(repo, redis_broker)
            wait_for(
                lambda: (
                    repo.get(execution.id).attempt_count == count
                    and repo.get(execution.id).status != "running"
                )
            )
            assert repo.get(execution.id).status == ("failed" if count == 3 else "pending")
            advance(clock, clock_file, 1)
        terminal = repo.get(execution.id)
        assert terminal.error.code == "attempts_exhausted"
        assert terminal.result is terminal.delivery_warning is None
        RedisPublisher(redis_broker).publish(execution)
        time.sleep(0.15)
        assert repo.get(execution.id) == terminal
