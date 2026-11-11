"""FND-01/07/08/11/12: real Redis and durable conditional delivery."""

import asyncio
import io
import time
from uuid import uuid4

from fastapi.testclient import TestClient
from resume_api.app import create_app
from resume_api.delivery import DiagnosticReconciler
from resume_core.broker import QUEUE, RedisPublisher
from resume_core.logging_policy import configure_logging
from resume_core.service import DiagnosticService


def intention(repo):
    return repo.create(uuid4(), uuid4()).execution


def take_message(broker):
    consumer = broker.consume(QUEUE, timeout=100)
    try:
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            message = next(consumer)
            if message is not None:
                consumer.ack(message)
                return message
        raise AssertionError("Message not delivered to real Redis")
    finally:
        consumer.close()


def test_real_broker_publishes_after_durable_intention(repository, redis_broker):
    repo, _ = repository
    execution = intention(repo)

    class VerifiedPublisher(RedisPublisher):
        def publish(self, due):
            assert repo.get(due.id).status == "pending"
            super().publish(due)

    asyncio.run(DiagnosticReconciler(repo, VerifiedPublisher(redis_broker)).tick())
    message = take_message(redis_broker)
    assert message.args == (str(execution.id), str(execution.request_id))
    assert message.kwargs == {}
    assert message.options["max_retries"] == 0
    assert repo.get(execution.id).status == "queued"
    assert repo.get(execution.id).delivery_warning is None


def test_real_redis_offline_warning_and_recovery_same_id(repository, redis_broker, isolated_redis):
    repo, clock = repository
    output = io.StringIO()
    configure_logging(stream=output)
    execution = intention(repo)
    reconciler = DiagnosticReconciler(repo, RedisPublisher(redis_broker))
    isolated_redis.stop()
    try:
        started = time.monotonic()
        asyncio.run(reconciler.tick())
        assert time.monotonic() - started < 1
        waiting = repo.get(execution.id)
        assert waiting.status == "pending"
        assert waiting.delivery_warning.model_dump() == {
            "code": "queue_unavailable",
            "message": "Queue is temporarily unavailable.",
        }
        assert waiting.error is None
    finally:
        isolated_redis.start()
    clock.advance(1)
    asyncio.run(reconciler.tick())
    restored = repo.get(execution.id)
    assert restored.id == execution.id
    assert restored.status == "queued"
    assert restored.delivery_warning is None
    assert restored.attempt_count == 0
    assert take_message(redis_broker).args[0] == str(execution.id)
    assert "Traceback" not in output.getvalue()


def test_redelivery_limited_to_once_per_second_and_queue_loss_recovered(repository, redis_broker):
    repo, clock = repository
    execution = intention(repo)
    reconciler = DiagnosticReconciler(repo, RedisPublisher(redis_broker))
    asyncio.run(reconciler.tick())
    assert repo.reserve_delivery() is None
    redis_broker.flush(QUEUE)
    clock.advance(0.999)
    asyncio.run(reconciler.tick())
    assert redis_broker.do_qsize(QUEUE) == 0
    clock.advance(0.001)
    asyncio.run(reconciler.tick())
    assert take_message(redis_broker).args[0] == str(execution.id)
    assert repo.get(execution.id).attempt_count == 0


def test_acknowledgement_cannot_regress_worker_claim_or_success(repository, redis_broker):
    repo, _ = repository
    execution = intention(repo)

    class ImmediateWorker(RedisPublisher):
        def publish(self, due):
            super().publish(due)
            lease = repo.claim(due.id)
            assert repo.complete(due.id, lease.token)

    asyncio.run(DiagnosticReconciler(repo, ImmediateWorker(redis_broker)).tick())
    terminal = repo.get(execution.id)
    assert terminal.status == "succeeded"
    assert terminal.attempt_count == 1
    assert not repo.finish_delivery(execution.id, False)
    assert repo.get(execution.id) == terminal


def test_delivery_warning_cannot_regress_running(repository):
    repo, _ = repository
    execution = intention(repo)
    lease = repo.claim(execution.id)
    assert not repo.finish_delivery(execution.id, False)
    assert not repo.finish_delivery(execution.id, True)
    assert repo.get(execution.id) == lease.execution


def test_total_deadline_reconciled_before_publication(repository, redis_broker):
    repo, clock = repository
    execution = intention(repo)
    clock.advance(120)
    asyncio.run(DiagnosticReconciler(repo, RedisPublisher(redis_broker)).tick())
    expired = repo.get(execution.id)
    assert expired.status == "failed"
    assert expired.error.code == "deadline_exceeded"
    assert redis_broker.do_qsize(QUEUE) == 0
    assert repo.reserve_delivery() is None


def test_api_startup_reconciles_before_serving(repository, redis_broker, tmp_path):
    repo, clock = repository
    execution = intention(repo)
    clock.advance(120)
    reconciler = DiagnosticReconciler(repo, RedisPublisher(redis_broker))
    app = create_app(
        service=DiagnosticService(repo),
        runtime_root=tmp_path,
        environment="test",
        reconciler=reconciler,
    )
    with TestClient(app, base_url="http://127.0.0.1:8000"):
        assert repo.get(execution.id).status == "failed"


def test_tick_offloads_blocking_publication(repository):
    repo, _ = repository
    execution = intention(repo)
    order = []

    class SlowPublisher:
        def publish(self, due):
            time.sleep(0.1)
            order.append("published")

    async def exercise():
        task = asyncio.create_task(DiagnosticReconciler(repo, SlowPublisher()).tick())
        await asyncio.sleep(0.01)
        order.append("responsive")
        await task

    asyncio.run(exercise())
    assert order == ["responsive", "published"]
    assert repo.get(execution.id).status == "queued"


def test_loop_reconciles_expiration_without_http_read(repository):
    repo, clock = repository
    execution = intention(repo)

    class Unavailable:
        def publish(self, due):
            raise ConnectionError("PRIVATE_SENTINEL")

    async def exercise():
        reconciler = DiagnosticReconciler(repo, Unavailable())
        stop = asyncio.Event()
        task = asyncio.create_task(reconciler.run(stop))
        clock.advance(120)
        await asyncio.sleep(1.05)
        stop.set()
        await task

    asyncio.run(exercise())
    assert repo.get(execution.id).status == "failed"
