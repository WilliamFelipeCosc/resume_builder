"""Explicit environment paths. Resolving configuration never reads app content."""

import os
import re
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path


def _safe_absolute(value: str | Path) -> Path:
    path = Path(value)
    if not path.is_absolute() or ".." in path.parts:
        raise ValueError("path must be absolute without traversal")
    for candidate in (path, *path.parents):
        if candidate.is_symlink():
            raise ValueError("symlink paths are not allowed")
    return path


@dataclass(frozen=True)
class EnvironmentPaths:
    data: Path
    config: Path
    cache: Path
    state: Path

    def create(self) -> None:
        for path in (self.data, self.config, self.cache, self.state):
            _safe_absolute(path)
            if path.exists():
                info = path.stat()
                if not path.is_dir() or info.st_uid != os.getuid() or info.st_mode & 0o077:
                    raise ValueError("application directory must be private and owned by this user")
            else:
                path.mkdir(mode=0o700, parents=True)


def resolve_paths(
    environment: str = "development",
    environ: Mapping[str, str] | None = None,
    *,
    test_root: Path | None = None,
) -> EnvironmentPaths:
    env = os.environ if environ is None else environ
    if not re.fullmatch(r"[a-z][a-z0-9_-]{0,31}", environment):
        raise ValueError("invalid environment name")
    if environment == "test":
        if test_root is None:
            raise ValueError("test_root is required for test environment")
        root = _safe_absolute(test_root)
        temporary = Path(tempfile.gettempdir()).resolve()
        if root == temporary or not root.is_relative_to(temporary):
            raise ValueError("test_root must be a dedicated temporary directory")
        return EnvironmentPaths(*(root / kind for kind in ("data", "config", "cache", "state")))
    if test_root is not None:
        raise ValueError("test_root is only accepted in test environment")
    home = _safe_absolute(env.get("HOME", str(Path.home())))
    defaults = (home / ".local/share", home / ".config", home / ".cache", home / ".local/state")
    keys = ("XDG_DATA_HOME", "XDG_CONFIG_HOME", "XDG_CACHE_HOME", "XDG_STATE_HOME")
    paths = [
        _safe_absolute(env.get(key, default)) / "resume-builder" / environment
        for key, default in zip(keys, defaults, strict=True)
    ]
    for path in paths:
        _safe_absolute(path)
    return EnvironmentPaths(*paths)
