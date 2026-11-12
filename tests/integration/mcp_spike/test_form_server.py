"""The demo server exposes only its fixed local HTML asset."""

import http.client
import threading

import pytest
from resume_mcp_server.form_server import create_form_server


@pytest.fixture
def server():
    instance = create_form_server(port=0)
    thread = threading.Thread(target=instance.serve_forever, daemon=True)
    thread.start()
    try:
        yield instance
    finally:
        instance.shutdown()
        thread.join()
        instance.server_close()


def request(server, path, method="GET", host=None):
    port = server.server_port
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=3)
    conn.request(method, path, headers={"Host": host or f"127.0.0.1:{port}"})
    response = conn.getresponse()
    status, content = response.status, response.read()
    conn.close()
    return status, content


@pytest.mark.parametrize("path", ["/", "/form.html"])
def test_only_form_is_served(server, path):
    status, body = request(server, path)
    assert status == 200
    assert b"fullName" in body and b"approvedAnswer" in body


@pytest.mark.parametrize(
    "path",
    ["/../context.json", "/%2e%2e/context.json", "/context.json", "/files/", "/?file=context.json"],
)
def test_arbitrary_paths_are_denied(server, path):
    status, body = request(server, path)
    assert status == 404
    assert b"Alex Exemplo" not in body


@pytest.mark.parametrize(
    "host",
    ["attacker.invalid", "localhost.attacker.invalid", "127.0.0.1.attacker.invalid", "localhost:1"],
)
def test_untrusted_host_is_denied(server, host):
    status, _ = request(server, "/", host=host)
    assert status == 403


def test_post_never_submits(server):
    status, _ = request(server, "/", method="POST")
    assert status == 405


def test_bind_address_is_loopback(server):
    assert server.server_address[0] == "127.0.0.1"
