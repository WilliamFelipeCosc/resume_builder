"""Local synthetic profiles and application-scoped authorization."""

import json
import os
import stat
from pathlib import Path
from typing import Literal

from pydantic import ConfigDict

from resume_core.mcp_spike.contracts import Capability, Contract
from resume_core.service import PermissionDenied


class Profile(Contract):
    model_config = ConfigDict(frozen=True)
    client_id: Literal["hermes", "codex"]
    application_ids: tuple[Literal["app-demo"], ...]
    capabilities: tuple[Capability, ...]


def require(profile: Profile | None, capability: str, application_id: str) -> None:
    if (
        profile is None
        or capability not in profile.capabilities
        or application_id not in profile.application_ids
    ):
        raise PermissionDenied("MCP access denied")


def _private_directory(path: Path) -> None:
    info = path.lstat()
    if (
        not stat.S_ISDIR(info.st_mode)
        or info.st_uid != os.getuid()
        or stat.S_IMODE(info.st_mode) != 0o700
    ):
        raise ValueError("invalid profile directory")


def load_profile(config_dir: Path, name: str) -> Profile:
    if name not in ("hermes", "codex") or not config_dir.is_absolute():
        raise ValueError("invalid profile selection")
    try:
        if any(part.is_symlink() for part in (config_dir, *config_dir.parents)):
            raise ValueError("symlink not allowed")
        profiles = config_dir / "profiles"
        _private_directory(config_dir)
        _private_directory(profiles)
        fd = os.open(profiles / f"{name}.json", os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(fd, "r", encoding="utf-8") as handle:
            info = os.fstat(handle.fileno())
            if (
                not stat.S_ISREG(info.st_mode)
                or info.st_uid != os.getuid()
                or stat.S_IMODE(info.st_mode) != 0o600
            ):
                raise ValueError("invalid profile file")
            profile = Profile.model_validate(json.load(handle))
        if profile.client_id != name:
            raise ValueError("profile identity mismatch")
        return profile
    except (OSError, ValueError) as exc:
        raise ValueError("invalid profile") from exc
