"""Explicit test-only real stack. Temporary synthetic data; no application control endpoint."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import uvicorn
from alembic import command
from resume_api.app import create_app
from resume_api.delivery import DiagnosticReconciler
from resume_core.broker import RedisPublisher, make_broker
from resume_core.database import make_engine, migration_config
from resume_core.logging_policy import configure_logging
from resume_core.repository import DiagnosticRepository
from resume_core.service import DiagnosticService

# This module is a test harness, not shipped application runtime.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests/integration"))
from redis_harness import DockerRedis  # noqa: E402

INFO_PATH = Path("/tmp/rb-web-harness.json")


def main():
    root = Path(__file__).resolve().parents[1]
    with (
        tempfile.TemporaryDirectory(prefix="rb-web-", dir="/tmp") as directory,
        DockerRedis() as redis,
    ):
        data = Path(directory)
        database = data / "diagnostics.sqlite3"
        engine = make_engine(database)
        command.upgrade(migration_config(engine), "head")
        broker = make_broker(redis.url, "web-harness")
        repo = DiagnosticRepository(engine)
        app = create_app(
            service=DiagnosticService(repo),
            runtime_root=data,
            environment="test",
            origin="http://127.0.0.1:8031",
            web_root=root / "apps/web/dist",
            reconciler=DiagnosticReconciler(repo, RedisPublisher(broker)),
        )
        worker = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "resume_worker",
                "--database",
                str(database),
                "--redis-url",
                redis.url,
                "--namespace",
                broker.namespace,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            INFO_PATH.write_text(
                json.dumps(
                    {
                        "socket": str(data / "resume-builder/test/bootstrap.sock"),
                        "workerPid": worker.pid,
                    }
                )
            )
            configure_logging()
            uvicorn.run(
                app,
                host="127.0.0.1",
                port=8031,
                log_config=None,
                access_log=False,
                proxy_headers=False,
            )
        finally:
            # The browser test may have paused this one owned Worker.
            import signal

            if worker.poll() is None:
                worker.send_signal(signal.SIGCONT)
                worker.terminate()
                worker.wait(timeout=10)
            INFO_PATH.unlink(missing_ok=True)
            broker.close()
            engine.dispose()


if __name__ == "__main__":
    main()
