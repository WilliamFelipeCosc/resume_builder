"""Isolated T4 Linux experiment. No app data, production auth, or browser control."""

import argparse
import json
import os
import secrets
import signal
import socket
import socketserver
import struct
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PAGE = b"""<!doctype html><meta charset="utf-8"><title>Bootstrap probe</title>
<p id="status">Unauthorized</p><script>
const ticket = new URLSearchParams(location.hash.slice(1)).get('bootstrap');
history.replaceState(null, '', location.pathname);
(async () => {
 if (ticket) await fetch('/bootstrap', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ticket})});
 const response = await fetch('/protected');
 document.querySelector('#status').textContent = response.ok ? 'Authorized' : 'Unauthorized';
})();
</script>"""


class Tickets:
    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.values = {}
        self.sessions = set()
        self.lock = threading.Lock()

    def issue(self):
        value = secrets.token_urlsafe(32)
        with self.lock:
            self.values[value] = self.clock() + 30
        return value

    def redeem(self, value):
        with self.lock:
            deadline = self.values.pop(value, None)
            if deadline is None or self.clock() >= deadline:
                return None
            session = secrets.token_urlsafe(32)
            self.sessions.add(session)
            return session


class Probe:
    def __init__(self, directory, expected_uid=None, port=0):
        self.directory = Path(directory)
        self.socket_path = self.directory / "bootstrap.sock"
        self.expected_uid = os.getuid() if expected_uid is None else expected_uid
        self.requested_port = port
        self.tickets = Tickets()
        self.peer_uids = []

    def __enter__(self):
        self.directory.mkdir(mode=0o700)
        probe = self

        class UnixHandler(socketserver.BaseRequestHandler):
            def handle(self):
                credentials = self.request.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12)
                _, uid, _ = struct.unpack("3i", credentials)
                probe.peer_uids.append(uid)
                response = (
                    {"ticket": probe.tickets.issue()}
                    if uid == probe.expected_uid
                    else {"error": "unauthorized"}
                )
                self.request.sendall(json.dumps(response).encode())

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def respond(self, status, body=b"", cookie=None, html=False):
                self.send_response(status)
                self.send_header("Content-Type", "text/html" if html else "application/json")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Referrer-Policy", "no-referrer")
                self.send_header(
                    "Content-Security-Policy", "default-src 'self'; script-src 'unsafe-inline'"
                )
                if cookie:
                    self.send_header(
                        "Set-Cookie", f"probe={cookie}; HttpOnly; SameSite=Strict; Path=/"
                    )
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                print(
                    json.dumps(
                        {"event": "probe_request", "requestId": str(uuid.uuid4()), "status": status}
                    ),
                    flush=True,
                )

            def allowed(self, write=False):
                origin = self.headers.get("Origin")
                return self.headers.get("Host") == f"127.0.0.1:{probe.port}" and (
                    origin == probe.origin if write else origin in (None, probe.origin)
                )

            def do_GET(self):
                if not self.allowed():
                    return self.respond(403)
                if self.path == "/":
                    return self.respond(200, PAGE, html=True)
                cookie = self.headers.get("Cookie", "")
                authorized = any(
                    part.strip().startswith("probe=") and part.strip()[6:] in probe.tickets.sessions
                    for part in cookie.split(";")
                )
                self.respond(200 if authorized else 401)

            def do_POST(self):
                if not self.allowed(write=True):
                    return self.respond(403)
                if self.path != "/bootstrap":
                    return self.respond(404)
                try:
                    size = int(self.headers.get("Content-Length", "0"))
                    if size < 0 or size > 1024:
                        return self.respond(413)
                    if self.headers.get("Content-Type") != "application/json":
                        return self.respond(422)
                    body = json.loads(self.rfile.read(size))
                    value = body["ticket"]
                    if not isinstance(value, str) or set(body) != {"ticket"}:
                        return self.respond(422)
                except ValueError, KeyError, TypeError:
                    return self.respond(422)
                session = probe.tickets.redeem(value)
                self.respond(200 if session else 401, cookie=session)

        self.unix = socketserver.UnixStreamServer(str(self.socket_path), UnixHandler)
        os.chmod(self.socket_path, 0o600)
        self.http = ThreadingHTTPServer(("127.0.0.1", self.requested_port), Handler)
        self.port = self.http.server_port
        self.origin = f"http://127.0.0.1:{self.port}"
        self.threads = [
            threading.Thread(target=server.serve_forever, daemon=True)
            for server in (self.unix, self.http)
        ]
        for thread in self.threads:
            thread.start()
        return self

    def __exit__(self, *args):
        for server in (self.unix, self.http):
            server.shutdown()
            server.server_close()
        for thread in self.threads:
            thread.join()
        self.socket_path.unlink()
        self.directory.rmdir()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", required=True)
    parser.add_argument("--port", type=int, default=0)
    args = parser.parse_args()
    stop = threading.Event()
    signal.signal(signal.SIGTERM, lambda *_: stop.set())
    with Probe(args.runtime, port=args.port) as probe:
        print(json.dumps({"origin": probe.origin}), flush=True)
        stop.wait()


if __name__ == "__main__":
    main()
