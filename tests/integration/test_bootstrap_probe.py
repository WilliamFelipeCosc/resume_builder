"""T4: Linux bootstrap viability; never touches application data."""

import concurrent.futures
import json
import os
import socket
from http.client import HTTPConnection

import pytest

from tools.bootstrap_probe.probe import Probe, Tickets


def ticket(path):
    with socket.socket(socket.AF_UNIX) as peer:
        peer.connect(str(path))
        return json.loads(peer.recv(1024))


def request(probe, method, path, body=None, headers=None):
    conn = HTTPConnection("127.0.0.1", probe.port)
    conn.request(method, path, body, headers or {})
    response = conn.getresponse()
    result = (response.status, dict(response.getheaders()), response.read())
    conn.close()
    return result


def redeem(probe, value):
    return request(
        probe,
        "POST",
        "/bootstrap",
        json.dumps({"ticket": value}),
        {"Origin": probe.origin, "Content-Type": "application/json"},
    )


def test_linux_peer_uid_and_permissions(tmp_path):
    with Probe(tmp_path / "probe") as probe:
        response = ticket(probe.socket_path)
        assert len(response["ticket"]) >= 43
        assert probe.peer_uids == [os.getuid()]
        assert probe.directory.stat().st_mode & 0o777 == 0o700
        assert probe.socket_path.stat().st_mode & 0o777 == 0o600


def test_wrong_peer_uid_is_rejected(tmp_path):
    with Probe(tmp_path / "probe", expected_uid=os.getuid() + 1) as probe:
        assert ticket(probe.socket_path) == {"error": "unauthorized"}
        assert probe.tickets.values == {}


def test_ticket_expires_at_exact_thirty_seconds():
    clock = [100.0]
    tickets = Tickets(lambda: clock[0])
    value = tickets.issue()
    clock[0] = 130.0
    assert tickets.redeem(value) is None


def test_ticket_before_deadline_is_valid():
    clock = [100.0]
    tickets = Tickets(lambda: clock[0])
    value = tickets.issue()
    clock[0] = 129.999
    assert tickets.redeem(value) is not None


def test_ticket_consumption_is_atomic():
    tickets = Tickets()
    value = tickets.issue()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        values = list(pool.map(lambda _: tickets.redeem(value), range(8)))
    assert sum(item is not None for item in values) == 1


def test_http_cookie_and_replay(tmp_path):
    with Probe(tmp_path / "probe") as probe:
        value = ticket(probe.socket_path)["ticket"]
        status, headers, _ = redeem(probe, value)
        assert status == 200
        assert "HttpOnly; SameSite=Strict; Path=/" in headers["Set-Cookie"]
        assert headers["Cache-Control"] == "no-store"
        assert redeem(probe, value)[0] == 401
        cookie = headers["Set-Cookie"].split(";")[0]
        assert request(probe, "GET", "/protected", headers={"Cookie": cookie})[0] == 200


def test_restart_invalidates_session(tmp_path):
    with Probe(tmp_path / "one") as probe:
        value = ticket(probe.socket_path)["ticket"]
        cookie = redeem(probe, value)[1]["Set-Cookie"].split(";")[0]
    with Probe(tmp_path / "two") as probe:
        assert request(probe, "GET", "/protected", headers={"Cookie": cookie})[0] == 401


def test_host_and_origin_rejected(tmp_path):
    with Probe(tmp_path / "probe") as probe:
        assert request(probe, "GET", "/", headers={"Host": "evil.example"})[0] == 403
        assert (
            request(probe, "POST", "/bootstrap", "{}", {"Origin": "https://evil.example"})[0] == 403
        )


def test_logs_never_contain_request_secrets(tmp_path, capsys):
    with Probe(tmp_path / "probe") as probe:
        value = ticket(probe.socket_path)["ticket"]
        status, headers, _ = redeem(probe, value)
        assert status == 200
        cookie = headers["Set-Cookie"].split(";")[0]
        request(probe, "GET", "/protected", headers={"Cookie": cookie})
        request(probe, "POST", "/bootstrap", "SYNTHETIC_SENTINEL", {"Origin": probe.origin})
    captured = capsys.readouterr()
    assert value not in captured.out + captured.err
    assert cookie not in captured.out + captured.err
    assert "SYNTHETIC_SENTINEL" not in captured.out + captured.err
    events = [json.loads(line) for line in captured.out.splitlines()]
    assert events
    assert all(set(event) == {"event", "requestId", "status"} for event in events)


def test_existing_or_symlink_runtime_is_refused(tmp_path):
    directory = tmp_path / "existing"
    directory.mkdir(mode=0o700)
    with pytest.raises(FileExistsError):
        Probe(directory).__enter__()
    link = tmp_path / "link"
    link.symlink_to(directory)
    with pytest.raises(FileExistsError):
        Probe(link).__enter__()
