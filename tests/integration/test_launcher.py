"""FND-13: local opening obtains only an ephemeral ticket from the trusted Unix peer."""

import os
from urllib.parse import parse_qs, urlparse

import pytest
from resume_api.launcher import get_ticket, launch
from resume_api.session import SessionChannel


def test_launch_opens_only_fragment_ticket_and_does_not_print(tmp_path, capsys):
    opened = []
    with SessionChannel(tmp_path, "test") as channel:
        launch(tmp_path, "test", opener=lambda url: opened.append(url) or True)
        assert len(opened) == 1
        url = urlparse(opened[0])
        assert url.scheme == "http" and url.netloc == "127.0.0.1:8000"
        assert url.path == "/" and url.query == ""
        ticket = parse_qs(url.fragment)["bootstrap"][0]
        assert channel.store.redeem(ticket) is not None
        assert channel.store.redeem(ticket) is None
    assert capsys.readouterr() == ("", "")


def test_launcher_checks_peer_uid(tmp_path):
    with SessionChannel(tmp_path, "test"):
        with pytest.raises(ValueError, match="peer"):
            get_ticket(tmp_path, "test", expected_uid=os.getuid() + 1)


def test_launcher_rejects_socket_symlink_and_insecure_permissions(tmp_path):
    with SessionChannel(tmp_path, "test") as channel:
        channel.socket_path.chmod(0o666)
        with pytest.raises(ValueError, match="socket"):
            get_ticket(tmp_path, "test")
        channel.socket_path.chmod(0o600)
    path = tmp_path / "resume-builder/test/bootstrap.sock"
    path.symlink_to(tmp_path / "absent")
    with pytest.raises(ValueError, match="socket"):
        get_ticket(tmp_path, "test")


def test_launcher_failure_does_not_echo_ticket(tmp_path):
    with SessionChannel(tmp_path, "test"):
        with pytest.raises(ValueError, match="browser") as error:
            launch(tmp_path, "test", opener=lambda url: False)
        assert "bootstrap=" not in str(error.value)


def test_launcher_rejects_nonlocal_origin_before_issuing_ticket(tmp_path):
    with SessionChannel(tmp_path, "test") as channel:
        with pytest.raises(ValueError, match="origin"):
            launch(tmp_path, "test", origin="https://evil.invalid")
        assert channel.store.ticket_count == 0


def test_default_opener_suppresses_child_output(tmp_path, monkeypatch):
    import subprocess
    from types import SimpleNamespace

    calls = []
    monkeypatch.setattr(
        "resume_api.launcher.subprocess.run",
        lambda args, **options: calls.append((args, options)) or SimpleNamespace(returncode=0),
    )
    with SessionChannel(tmp_path, "test"):
        launch(tmp_path, "test")
    assert calls[0][0][0] == "xdg-open"
    assert calls[0][1]["stdout"] == subprocess.DEVNULL
    assert calls[0][1]["stderr"] == subprocess.DEVNULL
