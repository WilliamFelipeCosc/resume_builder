"""Test-only orchestration of the real operator CLI, with temporary synthetic data."""

import json
import os
import signal
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests/integration"))
from redis_harness import DockerRedis  # noqa: E402

INFO_PATH = Path("/tmp/rb-web-harness.json")


def main():
    with (
        tempfile.TemporaryDirectory(prefix="rb-web-", dir="/tmp") as directory,
        tempfile.TemporaryFile(mode="w+") as api_logs,
        tempfile.TemporaryFile(mode="w+") as worker_logs,
        DockerRedis() as redis,
    ):
        data = Path(directory)
        env = {**os.environ, "XDG_RUNTIME_DIR": directory}
        base = [
            sys.executable,
            "-m",
            "resume_api",
            "--environment",
            "test",
            "--test-root",
            directory,
        ]
        migration = subprocess.run(
            [*base, "migrate"], env=env, capture_output=True, text=True, check=True
        )
        assert migration.stdout == ""
        options = ["--redis-url", redis.url, "--namespace", "web-harness"]
        worker = subprocess.Popen(
            [*base, "worker", *options],
            env=env,
            stdout=subprocess.PIPE,
            stderr=worker_logs,
            text=True,
        )
        api = None
        stop, restart = threading.Event(), threading.Event()
        signal.signal(signal.SIGTERM, lambda *_: stop.set())
        signal.signal(signal.SIGINT, lambda *_: stop.set())
        # Only this external harness handles restart; the application exposes no fault controls.
        signal.signal(signal.SIGHUP, lambda *_: restart.set())

        def start_api():
            process = subprocess.Popen(
                [*base, "serve", "--port", "8031", *options],
                env=env,
                stdout=subprocess.PIPE,
                stderr=api_logs,
                text=True,
            )
            temporary = INFO_PATH.with_suffix(".next")
            temporary.write_text(
                json.dumps(
                    {
                        "socket": str(data / "resume-builder/test/bootstrap.sock"),
                        "workerPid": worker.pid,
                        "apiPid": process.pid,
                        "harnessPid": os.getpid(),
                    }
                )
            )
            temporary.replace(INFO_PATH)
            return process

        def end_api(process):
            if process.poll() is None:
                process.terminate()
            stdout, _ = process.communicate(timeout=10)
            assert stdout == "" and process.returncode in (0, -signal.SIGTERM)

        try:
            api = start_api()
            while not stop.wait(0.05):
                if api.poll() is not None:
                    raise AssertionError("API CLI exited unexpectedly")
                if restart.is_set():
                    restart.clear()
                    end_api(api)
                    api = start_api()
        finally:
            try:
                if api is not None:
                    end_api(api)
            finally:
                try:
                    if worker.poll() is None:
                        worker.send_signal(signal.SIGCONT)
                        worker.terminate()
                    stdout, _ = worker.communicate(timeout=10)
                    assert stdout == "" and worker.returncode == 0
                finally:
                    INFO_PATH.unlink(missing_ok=True)
            for output in [api_logs, worker_logs]:
                output.seek(0)
                for line in output:
                    record = json.loads(line)
                    assert isinstance(record, dict) and "event" in record
                    assert "Traceback" not in line


if __name__ == "__main__":
    main()
