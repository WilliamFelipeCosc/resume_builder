"""Linux UID-bound bootstrap channel and API-instance memory sessions."""

import errno
import fcntl
import json
import os
import re
import secrets
import socket
import socketserver
import stat
import struct
import threading
import time
from pathlib import Path


class SessionStore:
    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self._tickets = {}
        self._sessions = set()
        self._lock = threading.Lock()

    @property
    def ticket_count(self):
        with self._lock:
            return len(self._tickets)

    def issue(self):
        ticket = secrets.token_urlsafe(32)
        with self._lock:
            now = self.clock()
            self._tickets = {key: ttl for key, ttl in self._tickets.items() if ttl > now}
            self._tickets[ticket] = now + 30
        return ticket

    def redeem(self, ticket):
        if not isinstance(ticket, str):
            return None
        with self._lock:
            expires = self._tickets.pop(ticket, None)
            if expires is None or self.clock() >= expires:
                return None
            session = secrets.token_urlsafe(32)
            self._sessions.add(session)
            return session

    def authorized(self, session):
        with self._lock:
            return isinstance(session, str) and session in self._sessions

    def clear(self):
        with self._lock:
            self._tickets.clear()
            self._sessions.clear()


def _private_directory(path):
    try:
        info = path.lstat()
    except OSError:
        raise ValueError("A private runtime directory is required") from None
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise ValueError("Unsafe runtime directory")
    # A symlink in an ancestor can redirect the otherwise valid final directory.
    if any(parent.is_symlink() for parent in [path, *path.parents]):
        raise ValueError("Unsafe runtime path")


class SessionChannel:
    def __init__(self, runtime_root, environment, *, store=None, expected_uid=None):
        root = Path(runtime_root)
        if not root.is_absolute() or not re.fullmatch(r"[a-z][a-z0-9-]{0,31}", environment):
            raise ValueError("Invalid runtime configuration")
        self.root = root
        self.directory = root / "resume-builder" / environment
        self.socket_path = self.directory / "bootstrap.sock"
        self.store = store or SessionStore()
        self.expected_uid = os.getuid() if expected_uid is None else expected_uid
        self._lock_fd = None
        self._server = None
        self._thread = None
        self._socket_inode = None

    def __enter__(self):
        _private_directory(self.root)
        for path in [self.directory.parent, self.directory]:
            path.mkdir(mode=0o700, exist_ok=True)
            _private_directory(path)
        lock_path = self.directory / "api.lock"
        try:
            self._lock_fd = os.open(lock_path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
            info = os.fstat(self._lock_fd)
            if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
                raise ValueError("Unsafe instance lock")
            try:
                fcntl.flock(self._lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise ValueError("An API instance is already running") from None
            self._prepare_socket()
            channel = self

            class Handler(socketserver.BaseRequestHandler):
                def handle(self):
                    credentials = self.request.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12)
                    _, uid, _ = struct.unpack("3i", credentials)
                    payload = (
                        {"ticket": channel.store.issue()}
                        if uid == channel.expected_uid
                        else {"error": "unauthorized"}
                    )
                    try:
                        self.request.sendall(json.dumps(payload).encode())
                    except OSError:
                        pass

            class Server(socketserver.ThreadingUnixStreamServer):
                daemon_threads = True

                def handle_error(self, request, client_address):
                    pass  # No raw exception output from the bootstrap boundary.

            self._server = Server(str(self.socket_path), Handler)
            os.chmod(self.socket_path, 0o600)
            self._socket_inode = self.socket_path.lstat().st_ino
            self._thread = threading.Thread(
                target=lambda: self._server.serve_forever(poll_interval=0.05), daemon=True
            )
            self._thread.start()
            return self
        except ValueError:
            self.close()
            raise
        except OSError:
            self.close()
            raise ValueError("Unsafe runtime channel or conflicting instance") from None

    def _prepare_socket(self):
        try:
            info = self.socket_path.lstat()
        except FileNotFoundError:
            return
        if not stat.S_ISSOCK(info.st_mode) or info.st_uid != os.getuid():
            raise ValueError("Unsafe runtime socket")
        with socket.socket(socket.AF_UNIX) as probe:
            probe.settimeout(0.2)
            try:
                probe.connect(str(self.socket_path))
            except OSError as error:
                if error.errno != errno.ECONNREFUSED:
                    raise ValueError("Cannot verify runtime socket") from None
            else:
                raise ValueError("A live socket is already present")
        self.socket_path.unlink()

    def close(self):
        if self._thread:
            self._server.shutdown()
            self._thread.join(timeout=2)
        if self._server:
            self._server.server_close()
        if self._socket_inode is not None:
            try:
                if self.socket_path.lstat().st_ino == self._socket_inode:
                    self.socket_path.unlink()
            except FileNotFoundError:
                pass
        if self._lock_fd is not None:
            os.close(self._lock_fd)
            self._lock_fd = None
        self.store.clear()

    def __exit__(self, *args):
        self.close()
