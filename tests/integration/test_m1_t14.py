import hashlib
import os

import pytest
from resume_core.sources.storage import SourceIntegrityError, SourceStorage


def test_m1_storage_reuses_digest_and_preserves_original(tmp_path):
    original = tmp_path / "original"
    original.write_bytes(b"synthetic source")
    storage = SourceStorage(tmp_path / "data")
    first = storage.install(original.read_bytes())
    second = storage.install(original.read_bytes())
    assert first == second
    assert first.sha256 == hashlib.sha256(b"synthetic source").hexdigest()
    assert first.storage_ref == first.sha256
    assert first.size == len(b"synthetic source")
    assert storage.read(first.storage_ref) == original.read_bytes()
    assert original.read_bytes() == b"synthetic source"


def test_m1_storage_refuses_corruption_and_missing(tmp_path):
    storage = SourceStorage(tmp_path / "data")
    manifest = storage.install(b"synthetic")
    (storage.root / manifest.storage_ref).write_bytes(b"corrupt")
    with pytest.raises(SourceIntegrityError):
        storage.read(manifest.storage_ref)
    with pytest.raises(SourceIntegrityError):
        storage.install(b"synthetic")
    with pytest.raises(SourceIntegrityError):
        storage.read("0" * 64)


def test_m1_storage_rejects_traversal_and_symlink(tmp_path):
    storage = SourceStorage(tmp_path / "data")
    with pytest.raises(SourceIntegrityError):
        storage.read("../original")
    digest = hashlib.sha256(b"synthetic").hexdigest()
    target = tmp_path / "target"
    target.write_bytes(b"synthetic")
    (storage.root / digest).symlink_to(target)
    with pytest.raises(SourceIntegrityError):
        storage.install(b"synthetic")
    (tmp_path / "link").symlink_to(storage.root, target_is_directory=True)
    with pytest.raises(ValueError):
        SourceStorage(tmp_path / "link")


def test_m1_storage_failure_before_install_leaves_no_object(tmp_path, monkeypatch):
    storage = SourceStorage(tmp_path / "data")

    def fail(*args, **kwargs):
        raise OSError("simulated crash")

    monkeypatch.setattr(os, "link", fail)
    with pytest.raises(OSError):
        storage.install(b"synthetic")
    assert list(storage.root.iterdir()) == []


def test_m1_storage_failure_after_install_leaves_valid_orphan(tmp_path, monkeypatch):
    storage = SourceStorage(tmp_path / "data")
    real_fsync = os.fsync

    def fail_directory(fd):
        if os.path.isdir(f"/proc/self/fd/{fd}"):
            raise OSError("simulated crash")
        real_fsync(fd)

    monkeypatch.setattr(os, "fsync", fail_directory)
    with pytest.raises(OSError):
        storage.install(b"synthetic")
    assert storage.read(hashlib.sha256(b"synthetic").hexdigest()) == b"synthetic"
