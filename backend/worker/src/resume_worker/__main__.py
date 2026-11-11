"""Explicit one-process/one-thread Worker. Redis must already be running."""

import argparse
import signal
import sys
import threading
from pathlib import Path

import structlog
from dramatiq import Worker
from resume_core.broker import make_broker
from resume_core.database import make_engine
from resume_core.logging_policy import configure_logging
from resume_core.repository import DiagnosticRepository

from resume_worker.diagnostic import create_actor


def main():
    configure_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--redis-url", default="redis://127.0.0.1:6379/0")
    parser.add_argument("--namespace", default="resume-builder-development")
    args = parser.parse_args()
    broker = make_broker(args.redis_url, args.namespace)
    engine = make_engine(args.database)
    create_actor(DiagnosticRepository(engine), broker)
    worker = Worker(broker, worker_threads=1, worker_timeout=100)
    stop = threading.Event()
    signal.signal(signal.SIGTERM, lambda *_: stop.set())
    signal.signal(signal.SIGINT, lambda *_: stop.set())
    try:
        worker.start()
        stop.wait()
    finally:
        worker.stop(timeout=2000)
        broker.client.close()
        engine.dispose()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        structlog.get_logger().error("internal_error", code="internal_error")
        sys.exit(1)
