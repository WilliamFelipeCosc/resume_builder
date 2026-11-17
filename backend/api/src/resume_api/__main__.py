"""Explicit local operation. Redis and migrations are never started by serve."""

import argparse
import fcntl
import os
import re
import sys
from pathlib import Path

import structlog
import uvicorn
from alembic import command
from resume_core.broker import RedisPublisher, make_broker
from resume_core.database import make_engine, migration_config
from resume_core.logging_policy import configure_logging
from resume_core.paths import resolve_paths
from resume_core.repository import DiagnosticRepository
from resume_core.service import DiagnosticService
from resume_core.sources.manual_notes import ManualNoteService
from resume_core.sources.storage import SourceStorage

from resume_api.app import create_app
from resume_api.delivery import DiagnosticReconciler
from resume_api.launcher import launch


def main():
    configure_logging()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--environment", default="development")
    parser.add_argument("--test-root", type=Path)
    commands = parser.add_subparsers(dest="action", required=True)
    commands.add_parser("migrate")
    opening = commands.add_parser("open")
    opening.add_argument("--port", type=int, default=8000)
    for name in ["serve", "worker"]:
        sub = commands.add_parser(name)
        sub.add_argument("--redis-url", default="redis://127.0.0.1:6379/0")
        sub.add_argument("--namespace")
        if name == "serve":
            sub.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,31}", args.environment):
        raise ValueError("Invalid environment")
    if hasattr(args, "port") and not 1 <= args.port <= 65535:
        raise ValueError("Invalid local port")
    if args.action == "open":
        launch(
            Path(os.environ["XDG_RUNTIME_DIR"]),
            args.environment,
            origin=f"http://127.0.0.1:{args.port}",
        )
        return
    paths = resolve_paths(args.environment, test_root=args.test_root)
    database = paths.data / "diagnostics.sqlite3"
    if args.action == "migrate":
        paths.create()
        lock = os.open(paths.data / "migration.lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            engine = make_engine(database)
            try:
                command.upgrade(migration_config(engine), "head")
            finally:
                engine.dispose()
        finally:
            os.close(lock)
        return
    if not database.is_file() or database.is_symlink():
        raise ValueError("Run the explicit migration command first")
    namespace = args.namespace or "resume-builder-" + args.environment
    if args.action == "worker":
        os.execv(
            sys.executable,
            [
                sys.executable,
                "-m",
                "resume_worker",
                "--database",
                str(database),
                "--redis-url",
                args.redis_url,
                "--namespace",
                namespace,
            ],
        )
    engine = make_engine(database)
    broker = make_broker(args.redis_url, namespace)
    repo = DiagnosticRepository(engine)
    app = create_app(
        service=DiagnosticService(repo),
        source_service=ManualNoteService(engine, SourceStorage(paths.data)),
        runtime_root=Path(os.environ["XDG_RUNTIME_DIR"]),
        environment=args.environment,
        origin=f"http://127.0.0.1:{args.port}",
        reconciler=DiagnosticReconciler(repo, RedisPublisher(broker)),
        web_root=Path(__file__).resolve().parents[4] / "apps/web/dist",
    )
    try:
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=args.port,
            log_config=None,
            access_log=False,
            proxy_headers=False,
        )
    finally:
        broker.client.close()
        engine.dispose()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        structlog.get_logger().error("internal_error", code="internal_error")
        sys.exit(1)
