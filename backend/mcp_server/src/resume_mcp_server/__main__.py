"""Explicit local lifecycle for the synthetic MCP spike."""

import argparse
import json
import os
import stat
import sys
from pathlib import Path

from alembic import command
from resume_core.mcp_spike.contracts import ApplicationContext
from resume_core.mcp_spike.database import make_engine, reports
from resume_core.mcp_spike.policy import load_profile
from resume_core.paths import EnvironmentPaths, resolve_paths
from sqlalchemy import select

from resume_mcp_server.migration import is_current, migration_config

FIXTURE = Path(__file__).resolve().parents[4] / "data/synthetic/mcp-spike/context.json"
CAPABILITIES = ["application_context:read", "application_progress:write"]


def _database_path(paths: EnvironmentPaths, *, must_exist: bool) -> Path:
    directory = paths.data.lstat()
    if (
        not stat.S_ISDIR(directory.st_mode)
        or directory.st_uid != os.getuid()
        or stat.S_IMODE(directory.st_mode) != 0o700
    ):
        raise ValueError("invalid data directory")
    path = paths.data / "mcp-spike.sqlite3"
    if path.is_symlink():
        raise ValueError("invalid database")
    if path.exists():
        info = path.stat()
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise ValueError("invalid database")
    elif must_exist:
        raise ValueError("database unavailable")
    return path


def _initialize(paths: EnvironmentPaths) -> None:
    paths.create()
    directory = paths.config / "profiles"
    if directory.is_symlink():
        raise ValueError("invalid profile directory")
    directory.mkdir(mode=0o700, exist_ok=True)
    info = directory.stat()
    if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
        raise ValueError("invalid profile directory")
    for name in ("hermes", "codex"):
        path = directory / f"{name}.json"
        if path.is_symlink():
            raise ValueError("invalid profile")
        if not path.exists():
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(
                    {
                        "clientId": name,
                        "applicationIds": ["app-demo"],
                        "capabilities": CAPABILITIES,
                    },
                    handle,
                )
        load_profile(paths.config, name)
    engine = make_engine(_database_path(paths, must_exist=False))
    try:
        command.upgrade(migration_config(engine), "head")
    finally:
        engine.dispose()


def _open(paths: EnvironmentPaths, profile_name: str):
    principal = load_profile(paths.config, profile_name)
    engine = make_engine(_database_path(paths, must_exist=True))
    try:
        if not is_current(engine):
            raise ValueError("schema not current")
    except Exception:
        engine.dispose()
        raise
    return principal, engine


def _serve(paths: EnvironmentPaths, name: str) -> None:
    from resume_core.logging_policy import configure_mcp_logging

    configure_mcp_logging()
    from resume_core.mcp_spike.repository import Repository
    from resume_core.mcp_spike.service import ContextService, ProgressService

    from resume_mcp_server.server import create_server

    principal, engine = _open(paths, name)
    try:

        def load_context(application_id: str) -> ApplicationContext | None:
            context = ApplicationContext.model_validate_json(FIXTURE.read_text(encoding="utf-8"))
            return context if application_id == context.application_id else None

        service = ContextService(load_context)
        create_server(principal, service, ProgressService(Repository(engine))).run(
            transport="stdio", show_banner=False
        )
    finally:
        engine.dispose()


def _reports(paths: EnvironmentPaths, name: str) -> None:
    principal, engine = _open(paths, name)
    try:
        with engine.connect() as connection:
            rows = (
                connection.execute(
                    select(reports).where(reports.c.client_id == principal.client_id)
                )
                .mappings()
                .all()
            )
        print(json.dumps([dict(row) for row in rows], ensure_ascii=False))
    finally:
        engine.dispose()


def main() -> int:
    parser = argparse.ArgumentParser(description="Synthetic MCP spike lifecycle")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init", help="Initialize the isolated synthetic environment")
    for name in ("serve", "reports"):
        sub.add_parser(name).add_argument("--profile", choices=("hermes", "codex"), required=True)
    args = parser.parse_args()
    os.umask(0o077)
    try:
        paths = resolve_paths("mcp-spike")
        if args.command == "init":
            _initialize(paths)
        elif args.command == "serve":
            _serve(paths, args.profile)
        else:
            _reports(paths, args.profile)
        return 0
    except Exception:
        print("MCP spike operation failed.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
