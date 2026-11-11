"""Open the same-origin Web application using a one-use UID-bound bootstrap ticket."""

import argparse
import json
import os
import re
import socket
import stat
import struct
import subprocess
from pathlib import Path

from resume_api.session import SessionChannel, _private_directory


def get_ticket(runtime_root, environment, *, expected_uid=None):
    channel = SessionChannel(runtime_root, environment)
    for path in [channel.root, channel.directory.parent, channel.directory]:
        _private_directory(path)
    info = channel.socket_path.lstat()
    uid = os.getuid() if expected_uid is None else expected_uid
    if not stat.S_ISSOCK(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise ValueError("Unsafe session socket")
    with socket.socket(socket.AF_UNIX) as client:
        client.settimeout(1)
        client.connect(str(channel.socket_path))
        _, peer_uid, _ = struct.unpack(
            "3i", client.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12)
        )
        if peer_uid != uid:
            raise ValueError("Unexpected session peer")
        payload = bytearray()
        while len(payload) <= 512:
            chunk = client.recv(513 - len(payload))
            if not chunk:
                break
            payload.extend(chunk)
        if len(payload) > 512:
            raise ValueError("Invalid session response")
        try:
            value = json.loads(payload)
        except ValueError, UnicodeError:
            raise ValueError("Invalid session response") from None
        ticket = value.get("ticket") if isinstance(value, dict) else None
        if not isinstance(ticket, str) or not re.fullmatch(r"[A-Za-z0-9_-]{43}", ticket):
            raise ValueError("Invalid session response")
        return ticket


def _default_opener(url):
    # xdg-open may echo its URL on failure; child streams must never expose the ticket.
    return (
        subprocess.run(
            ["xdg-open", url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=10,
            check=False,
        ).returncode
        == 0
    )


def launch(runtime_root, environment, *, origin="http://127.0.0.1:8000", opener=None):
    if not re.fullmatch(r"http://127\.0\.0\.1:[1-9][0-9]{0,4}", origin):
        raise ValueError("Invalid local origin")
    if int(origin.rsplit(":", 1)[1]) > 65535:
        raise ValueError("Invalid local origin")
    ticket = get_ticket(runtime_root, environment)
    try:
        opened = (opener or _default_opener)(origin + "/#bootstrap=" + ticket)
    except Exception:
        raise ValueError("Cannot open the default browser") from None
    if not opened:
        raise ValueError("Cannot open the default browser")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--environment", default="development")
    args = parser.parse_args()
    try:
        launch(Path(os.environ["XDG_RUNTIME_DIR"]), args.environment)
    except Exception:
        # A browser error may contain its URL; never print exception text.
        parser.exit(1, "Cannot open the local application. Check the API and runtime directory.\n")


if __name__ == "__main__":
    main()
