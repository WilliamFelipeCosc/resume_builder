"""FND-13/15/16: real Unix peer auth and private ephemeral session lifecycle."""

import json
import os
import socket
from concurrent.futures import ThreadPoolExecutor

import pytest
from resume_api.session import SessionChannel, SessionStore


def read_ticket(path):
    with socket.socket(socket.AF_UNIX) as peer:
        peer.settimeout(2)
        peer.connect(str(path))
        return json.loads(peer.recv(1024))


def test_real_uid_channel_permissions_and_cleanup(tmp_path):
    with SessionChannel(tmp_path, "development") as channel:
        assert channel.directory.stat().st_mode & 0o777 == 0o700
        assert channel.socket_path.stat().st_mode & 0o777 == 0o600
        ticket = read_ticket(channel.socket_path)["ticket"]
        assert len(ticket) >= 43
        session = channel.store.redeem(ticket)
        assert channel.store.authorized(session)
        assert channel.store.redeem(ticket) is None
    assert not channel.socket_path.exists()
    assert not channel.store.authorized(session)


def test_uid_mismatch_cannot_mint_ticket(tmp_path):
    with SessionChannel(tmp_path, "test", expected_uid=os.getuid() + 1) as channel:
        assert read_ticket(channel.socket_path) == {"error": "unauthorized"}
        assert channel.store.ticket_count == 0


def test_ticket_expiration_exact_boundary():
    now = [0.0]
    store = SessionStore(clock=lambda: now[0])
    ticket = store.issue()
    now[0] = 30.0
    assert store.redeem(ticket) is None
    assert store.ticket_count == 0


def test_ticket_atomic_redemption():
    store = SessionStore()
    ticket = store.issue()
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(store.redeem, [ticket] * 8))
    assert sum(item is not None for item in results) == 1


def test_restart_discards_sessions_and_tickets(tmp_path):
    with SessionChannel(tmp_path, "test") as first:
        ticket = first.store.issue()
        session = first.store.redeem(first.store.issue())
    with SessionChannel(tmp_path, "test") as second:
        assert not second.store.authorized(session)
        assert second.store.redeem(ticket) is None


def test_second_instance_preserves_live_socket(tmp_path):
    with SessionChannel(tmp_path, "test") as first:
        inode = first.socket_path.stat().st_ino
        with pytest.raises(ValueError, match="instance"):
            with SessionChannel(tmp_path, "test"):
                pass
        assert first.socket_path.stat().st_ino == inode
        assert "ticket" in read_ticket(first.socket_path)


@pytest.mark.parametrize("mode", [0o755, 0o777])
def test_insecure_runtime_rejected(tmp_path, mode):
    tmp_path.chmod(mode)
    with pytest.raises(ValueError, match="runtime"):
        with SessionChannel(tmp_path, "test"):
            pass


def test_symlink_runtime_rejected(tmp_path):
    link = tmp_path / "link"
    link.symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(ValueError, match="runtime"):
        with SessionChannel(link, "test"):
            pass


@pytest.mark.parametrize("kind", ["lock", "socket"])
def test_symlink_artifact_rejected(tmp_path, kind):
    directory = tmp_path / "resume-builder" / "test"
    directory.mkdir(parents=True, mode=0o700)
    (directory.parent).chmod(0o700)
    target = tmp_path / "sentinel"
    target.write_text("unchanged")
    (directory / ("api.lock" if kind == "lock" else "bootstrap.sock")).symlink_to(target)
    with pytest.raises(ValueError):
        with SessionChannel(tmp_path, "test"):
            pass
    assert target.read_text() == "unchanged"


def test_stale_socket_recovered_under_lock(tmp_path):
    directory = tmp_path / "resume-builder" / "test"
    directory.mkdir(parents=True, mode=0o700)
    directory.parent.chmod(0o700)
    path = directory / "bootstrap.sock"
    with socket.socket(socket.AF_UNIX) as peer:
        peer.bind(str(path))
    with SessionChannel(tmp_path, "test") as channel:
        assert "ticket" in read_ticket(channel.socket_path)


def test_live_socket_without_lock_is_not_removed(tmp_path):
    directory = tmp_path / "resume-builder" / "test"
    directory.mkdir(parents=True, mode=0o700)
    directory.parent.chmod(0o700)
    path = directory / "bootstrap.sock"
    with socket.socket(socket.AF_UNIX) as peer:
        peer.bind(str(path))
        peer.listen()
        inode = path.stat().st_ino
        with pytest.raises(ValueError, match="live"):
            with SessionChannel(tmp_path, "test"):
                pass
        assert path.stat().st_ino == inode


def test_missing_runtime_has_no_fallback(tmp_path):
    with pytest.raises(ValueError):
        with SessionChannel(tmp_path / "missing", "test"):
            pass
