"""Test-only Worker fault harness; production actor/API expose no control fields."""

import json
import signal
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

import dramatiq
from dramatiq import Worker
from resume_core.broker import ACTOR, QUEUE, make_broker
from resume_core.contracts import DiagnosticResult
from resume_core.database import make_engine
from resume_core.logging_policy import configure_logging
from resume_core.repository import DiagnosticRepository
from resume_worker.diagnostic import process_diagnostic


def main():
    database, redis_url, namespace, clock_path, control_path, mode = sys.argv[1:]
    control, clock_file = Path(control_path), Path(clock_path)
    engine = make_engine(Path(database))
    repo = DiagnosticRepository(
        engine, clock=lambda: datetime.fromisoformat(json.loads(clock_file.read_text()))
    )
    broker = make_broker(redis_url, namespace)

    def fixture():
        (control / "claimed").touch()
        if mode == "fail":
            raise RuntimeError("PRIVATE_SENTINEL_CONTROLLED_FAILURE")
        if mode == "block":
            while not (control / "release").exists():
                time.sleep(0.01)
        return DiagnosticResult()

    @dramatiq.actor(broker=broker, actor_name=ACTOR, queue_name=QUEUE, max_retries=0)
    def actor(execution_id, request_id):
        outcome = process_diagnostic(repo, execution_id, request_id, fixture=fixture)
        temporary = control / "outcome.next"
        temporary.write_text(json.dumps(outcome))
        temporary.replace(control / "outcome")

    configure_logging()
    worker = Worker(broker, worker_threads=1, worker_timeout=50)
    stop = threading.Event()
    signal.signal(signal.SIGTERM, lambda *_: stop.set())
    worker.start()
    try:
        stop.wait()
    finally:
        worker.stop(timeout=2000)
        broker.client.close()
        engine.dispose()


if __name__ == "__main__":
    main()
