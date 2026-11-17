"""Input authorization and budgets apply before parser access."""

import asyncio
import json

from resume_api.app import Boundary
from resume_core.service import Principal


class Sessions:
    def authorized(self, value):
        return value is not None and value.startswith("valid")


def run_request(
    boundary,
    path,
    *,
    cookie=True,
    chunks=(b"{}",),
    content_type="application/json",
    session="valid",
):
    messages = []
    reads = 0
    scope = {
        "type": "http",
        "method": "POST",
        "path": path,
        "headers": [
            (b"host", b"127.0.0.1:8000"),
            (b"origin", b"http://127.0.0.1:8000"),
            (b"content-type", content_type.encode()),
        ]
        + ([(b"cookie", f"resume_session={session}".encode())] if cookie else []),
    }

    async def receive():
        nonlocal reads
        index = reads
        reads += 1
        return {"type": "http.request", "body": chunks[index], "more_body": index < len(chunks) - 1}

    async def send(message):
        messages.append(message)

    asyncio.run(boundary(scope, receive, send))
    start = next(item for item in messages if item["type"] == "http.response.start")
    body = b"".join(
        item.get("body", b"") for item in messages if item["type"] == "http.response.body"
    )
    return start, body, reads


def boundary(capabilities):
    async def app(scope, receive, send):
        await receive()
        await send({"type": "http.response.start", "status": 204, "headers": []})
        await send({"type": "http.response.body", "body": b""})

    return Boundary(
        app,
        sessions=Sessions(),
        origin="http://127.0.0.1:8000",
        principal_factory=lambda: Principal("test", frozenset(capabilities)),
    )


def test_missing_session_or_capability_reads_no_bytes():
    guard = boundary(set())
    for cookie, status in [(False, 401), (True, 403)]:
        start, _, reads = run_request(guard, "/api/career/profiles", cookie=cookie)
        assert start["status"] == status
        assert reads == 0


def test_chunked_limit_and_existing_m0_budget():
    guard = boundary({"career:write"})
    start, _, reads = run_request(guard, "/api/career/profiles", chunks=(b"x" * (256 * 1024), b"x"))
    assert start["status"] == 413 and reads == 2
    start, _, reads = run_request(guard, "/api/diagnostics", chunks=(b"x" * 1025,))
    assert start["status"] == 413 and reads == 1
    start, _, _ = run_request(guard, "/api/career/profiles", chunks=(b"x" * (256 * 1024),))
    assert start["status"] == 204


def test_rate_limit_and_busy_prepare_are_explicit_before_body():
    guard = boundary({"career:write", "import:write"})
    for _ in range(120):
        assert run_request(guard, "/api/career/profiles")[0]["status"] == 204
    start, body, reads = run_request(guard, "/api/career/profiles")
    assert start["status"] == 429 and reads == 0
    assert json.loads(body)["error"]["code"] == "rate_limited"
    assert (b"retry-after", b"60") in start["headers"]
    guard = boundary({"import:write"})
    guard.preparing = True
    start, _, reads = run_request(
        guard, "/api/imports", content_type="multipart/form-data; boundary=demo"
    )
    assert start["status"] == 429 and reads == 0


def test_media_and_upload_total_limit():
    guard = boundary({"import:write"})
    start, _, _ = run_request(guard, "/api/imports")
    assert start["status"] == 415
    start, _, reads = run_request(
        guard,
        "/api/imports",
        content_type="multipart/form-data; boundary=demo",
        chunks=(b"x" * (12 * 1024 * 1024), b"x"),
    )
    assert start["status"] == 413 and reads == 2


def test_review_decisions_require_review_capability_before_body():
    guard = boundary({"career:write"})
    start, _, reads = run_request(guard, "/api/career/proposals/example/decisions")
    assert start["status"] == 403 and reads == 0


def test_import_session_global_limits_and_expiry(monkeypatch):
    clock = [100.0]
    monkeypatch.setattr("resume_api.app.time.monotonic", lambda: clock[0])
    guard = boundary({"import:write"})
    for session in ("valid-a", "valid-b"):
        for _ in range(5):
            assert (
                run_request(
                    guard,
                    "/api/imports",
                    session=session,
                    content_type="multipart/form-data; boundary=x",
                )[0]["status"]
                == 204
            )
    start, _, reads = run_request(
        guard, "/api/imports", session="valid-a", content_type="multipart/form-data; boundary=x"
    )
    assert start["status"] == 429 and reads == 0
    start, _, reads = run_request(
        guard, "/api/imports", session="valid-c", content_type="multipart/form-data; boundary=x"
    )
    assert start["status"] == 429 and reads == 0
    clock[0] += 61
    assert (
        run_request(
            guard, "/api/imports", session="valid-a", content_type="multipart/form-data; boundary=x"
        )[0]["status"]
        == 204
    )


def test_prepare_slot_released_on_exception_and_disconnect():
    async def failing(scope, receive, send):
        raise RuntimeError("PRIVATE_SENTINEL")

    guard = Boundary(
        failing,
        sessions=Sessions(),
        origin="http://127.0.0.1:8000",
        principal_factory=lambda: Principal("test", frozenset({"import:write"})),
    )
    start, body, _ = run_request(
        guard, "/api/imports", content_type="multipart/form-data; boundary=x"
    )
    assert start["status"] == 500 and b"PRIVATE_SENTINEL" not in body
    assert guard.preparing is False

    async def disconnected():
        scope = {
            "type": "http",
            "method": "POST",
            "path": "/api/imports",
            "headers": [
                (b"host", b"127.0.0.1:8000"),
                (b"origin", b"http://127.0.0.1:8000"),
                (b"cookie", b"resume_session=valid"),
            ],
        }

        async def receive():
            return {"type": "http.disconnect"}

        async def send(message):
            raise AssertionError("disconnect must not respond")

        await guard(scope, receive, send)

    asyncio.run(disconnected())
    assert guard.preparing is False


def test_simultaneous_prepare_rejects_before_reading():
    async def scenario():
        entered, release = asyncio.Event(), asyncio.Event()

        async def app(scope, receive, send):
            entered.set()
            await release.wait()
            await send({"type": "http.response.start", "status": 204, "headers": []})
            await send({"type": "http.response.body", "body": b""})

        guard = Boundary(
            app,
            sessions=Sessions(),
            origin="http://127.0.0.1:8000",
            principal_factory=lambda: Principal("test", frozenset({"import:write"})),
        )

        def scope():
            return {
                "type": "http",
                "method": "POST",
                "path": "/api/imports",
                "headers": [
                    (b"host", b"127.0.0.1:8000"),
                    (b"origin", b"http://127.0.0.1:8000"),
                    (b"cookie", b"resume_session=valid"),
                    (b"content-type", b"multipart/form-data; boundary=x"),
                ],
            }

        async def first_receive():
            return {"type": "http.request", "body": b"", "more_body": False}

        async def no_read():
            raise AssertionError("second request read body")

        async def discard(message):
            pass

        messages = []

        async def collect(message):
            messages.append(message)

        task = asyncio.create_task(guard(scope(), first_receive, discard))
        await entered.wait()
        await guard(scope(), no_read, collect)
        assert messages[0]["status"] == 429
        release.set()
        await task
        assert guard.preparing is False

    asyncio.run(scenario())
