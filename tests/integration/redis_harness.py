"""Explicit test-only Docker lifecycle. Application code never invokes Docker."""

import socket
import subprocess
import time
from uuid import uuid4

from redis import Redis

REDIS_IMAGE = "redis@sha256:71885d8cc6e42f2bc0aa2eb853bfc4be200b5108a46ac50e117ae1df0531fb80"


class DockerRedis:
    def __enter__(self):
        with socket.socket(socket.AF_INET) as reservation:
            reservation.bind(("127.0.0.1", 0))
            port = reservation.getsockname()[1]
        self.container = subprocess.check_output(
            [
                "docker",
                "run",
                "--detach",
                "--name",
                "rb-test-" + uuid4().hex,
                "--publish",
                f"127.0.0.1:{port}:6379",
                "--tmpfs",
                "/data:rw,noexec,nosuid,size=16m",
                REDIS_IMAGE,
                "redis-server",
                "--save",
                "",
                "--appendonly",
                "no",
            ],
            text=True,
        ).strip()
        try:
            address = subprocess.check_output(
                ["docker", "port", self.container, "6379"], text=True
            ).strip()
            self.url = "redis://" + address + "/0"
            self.ready()
            return self
        except BaseException:
            self.__exit__()
            raise

    def ready(self):
        client = Redis.from_url(self.url, socket_connect_timeout=0.2, socket_timeout=0.2)
        try:
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                try:
                    if client.ping():
                        return
                except OSError:
                    pass
                except Exception:
                    pass
                time.sleep(0.05)
            raise RuntimeError("Isolated Redis did not start")
        finally:
            client.close()

    def stop(self):
        subprocess.run(
            ["docker", "stop", "--time", "1", self.container], check=True, capture_output=True
        )

    def start(self):
        subprocess.run(["docker", "start", self.container], check=True, capture_output=True)
        self.ready()

    def __exit__(self, *args):
        subprocess.run(["docker", "rm", "--force", self.container], check=True, capture_output=True)
