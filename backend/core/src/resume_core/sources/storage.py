"""Durable, content-addressed storage for private source bytes."""

import hashlib
import os
import re
import secrets
import stat
from dataclasses import dataclass
from pathlib import Path

from resume_core.paths import _safe_absolute


class SourceIntegrityError(ValueError):
    """A source is missing, unsafe, or does not match its digest."""


@dataclass(frozen=True)
class SourceManifest:
    sha256: str
    storage_ref: str
    size: int


class SourceStorage:
    def __init__(self, data_directory: Path):
        self.root = _safe_absolute(data_directory) / "sources"
        _safe_absolute(self.root)
        self.root.mkdir(mode=0o700, parents=True, exist_ok=True)
        info = self.root.stat(follow_symlinks=False)
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise SourceIntegrityError("unsafe source directory")

    @staticmethod
    def _validate_ref(ref: str) -> None:
        if not re.fullmatch(r"[0-9a-f]{64}", ref):
            raise SourceIntegrityError("invalid source reference")

    def read(self, ref: str) -> bytes:
        self._validate_ref(ref)
        try:
            directory = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                fd = os.open(ref, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
                with os.fdopen(fd, "rb") as stream:
                    if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                        raise SourceIntegrityError("unsafe source")
                    data = stream.read()
            finally:
                os.close(directory)
        except OSError as exc:
            raise SourceIntegrityError("source unavailable") from exc
        if hashlib.sha256(data).hexdigest() != ref:
            raise SourceIntegrityError("source integrity failure")
        return data

    def install(self, data: bytes) -> SourceManifest:
        digest = hashlib.sha256(data).hexdigest()
        directory = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        temporary = f".source-{secrets.token_hex(16)}"
        try:
            fd = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600, dir_fd=directory)
            with os.fdopen(fd, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            try:
                # link is an atomic, no-overwrite installation on the same filesystem.
                os.link(temporary, digest, src_dir_fd=directory, dst_dir_fd=directory)
            except FileExistsError:
                if self.read(digest) != data:
                    raise SourceIntegrityError("source integrity failure")
            os.fsync(directory)
            return SourceManifest(digest, digest, len(data))
        finally:
            try:
                os.unlink(temporary, dir_fd=directory)
            except FileNotFoundError:
                pass
            os.close(directory)
