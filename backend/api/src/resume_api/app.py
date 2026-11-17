"""Same-origin FastAPI boundary. Authorization precedes bounded body parsing."""

import asyncio
import re
from contextlib import asynccontextmanager
from http.cookies import CookieError, SimpleCookie
from pathlib import Path
from typing import Literal
from uuid import UUID, uuid4

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field
from resume_core.contracts import DiagnosticCreate, DiagnosticResponse
from resume_core.repository import ActiveDiagnosticConflict
from resume_core.service import Principal
from starlette.exceptions import HTTPException as StarletteHTTPException

from resume_api.errors import ERRORS, HttpErrorResponse, error_response
from resume_api.session import SessionChannel, SessionStore

COOKIE_NAME = "resume_session"


class HealthResponse(BaseModel):
    status: Literal["ok"]


ERROR_RESPONSES = {code: {"model": HttpErrorResponse} for code in ERRORS}
SESSION_SECURITY = {"security": [{"LocalSession": []}]}


class BootstrapRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    ticket: str = Field(max_length=128)


class BootstrapResponse(BaseModel):
    authorized: bool


class Boundary:
    def __init__(self, app, *, sessions, origin):
        self.app, self.sessions, self.origin = app, sessions, origin
        self.host = origin.removeprefix("http://")

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        request_id = str(uuid4())
        scope.setdefault("state", {})["request_id"] = request_id
        headers = {}
        duplicate = False
        for key, value in scope["headers"]:
            key = key.lower()
            if (
                key in {b"host", b"origin", b"cookie", b"content-type", b"content-length"}
                and key in headers
            ):
                duplicate = True
            headers[key] = value.decode("latin1")
        path, method = scope["path"], scope["method"]
        origin = headers.get(b"origin")
        status = 500
        started = False

        async def safe_send(message):
            nonlocal status, started
            if message["type"] == "http.response.start":
                status = message["status"]
                started = True
                additions = [
                    (b"cache-control", b"no-store"),
                    (b"referrer-policy", b"no-referrer"),
                    (
                        b"content-security-policy",
                        b"default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'",
                    ),
                    (b"x-request-id", request_id.encode()),
                ]
                keys = {key for key, _ in additions}
                message["headers"] = [
                    (key, value)
                    for key, value in message.get("headers", [])
                    if key.lower() not in keys
                ] + additions
            await send(message)

        async def reject(code):
            await error_response(code, request_id)(scope, receive, safe_send)

        try:
            if duplicate or headers.get(b"host") != self.host or origin not in (None, self.origin):
                return await reject(403)
            if method not in {"GET", "HEAD", "OPTIONS"} and origin != self.origin:
                return await reject(403)
            public = path in {"/api/health", "/api/session/bootstrap", "/"} or path.startswith(
                "/assets/"
            )
            if not public:
                cookie = SimpleCookie()
                try:
                    cookie.load(headers.get(b"cookie", ""))
                except CookieError:
                    return await reject(401)
                morsel = cookie.get(COOKIE_NAME)
                if not self.sessions.authorized(morsel.value if morsel else None):
                    return await reject(401)
                scope["state"]["principal"] = Principal(
                    "local-user", frozenset({"diagnostic:read", "diagnostic:write"})
                )
            body = bytearray()
            try:
                length = int(headers.get(b"content-length", "0"))
            except ValueError:
                return await reject(422)
            if length < 0:
                return await reject(422)
            if length > 1024:
                return await reject(413)
            while True:
                message = await receive()
                if message["type"] == "http.disconnect":
                    return
                body.extend(message.get("body", b""))
                if len(body) > 1024:
                    return await reject(413)
                if not message.get("more_body", False):
                    break
            if method not in {"GET", "HEAD", "OPTIONS"} and (
                headers.get(b"content-type", "").split(";", 1)[0].strip().lower()
                != "application/json"
            ):
                return await reject(422)
            consumed = False

            async def buffered_receive():
                nonlocal consumed
                if not consumed:
                    consumed = True
                    return {"type": "http.request", "body": bytes(body), "more_body": False}
                return await receive()

            await self.app(scope, buffered_receive, safe_send)
        except Exception:
            structlog.get_logger().error(
                "internal_error", request_id=request_id, code="internal_error"
            )
            if not started:
                await reject(500)
        finally:
            structlog.get_logger().info(
                "request_completed",
                request_id=request_id,
                method=method,
                path=path,
                status_code=status,
            )


def create_app(
    *,
    service,
    runtime_root=None,
    environment="development",
    origin="http://127.0.0.1:8000",
    reconciler=None,
    web_root=None,
):
    if (
        not re.fullmatch(r"http://127\.0\.0\.1:[1-9][0-9]{0,4}", origin)
        or int(origin.rsplit(":", 1)[1]) > 65535
    ):
        raise ValueError("Only an explicit loopback origin is allowed")
    sessions = SessionStore()

    @asynccontextmanager
    async def lifespan(app):
        if runtime_root is None:
            raise ValueError("A secure XDG runtime directory is required")
        with SessionChannel(runtime_root, environment, store=sessions) as channel:
            app.state.channel = channel
            stop = asyncio.Event()
            task = None
            if reconciler is not None:
                await reconciler.tick()
                task = asyncio.create_task(reconciler.run(stop))
            try:
                yield
            finally:
                stop.set()
                if task is not None:
                    await task
        sessions.clear()

    app = FastAPI(
        title="Resume Builder M0",
        version="0.1.0",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=lifespan,
        responses=ERROR_RESPONSES,
    )
    app.state.sessions, app.state.service = sessions, service
    app.state.reconciler = reconciler
    app.add_middleware(Boundary, sessions=sessions, origin=origin)

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request, error):
        if error.status_code in ERRORS:
            return error_response(error.status_code, request.state.request_id)
        return error_response(500, request.state.request_id)

    @app.exception_handler(RequestValidationError)
    async def invalid_request(request, error):
        return error_response(
            422,
            request.state.request_id,
            fields=tuple(str(item["loc"][-1]) for item in error.errors() if item.get("loc")),
        )

    @app.exception_handler(Exception)
    async def unexpected_error(request, error):
        return error_response(500, request.state.request_id)

    @app.get("/api/health", response_model=HealthResponse, operation_id="get_health")
    async def health():
        return HealthResponse(status="ok")

    @app.get("/openapi.json", include_in_schema=False)
    async def schema_document():
        return JSONResponse(app.openapi())

    @app.get("/docs", include_in_schema=False, response_class=HTMLResponse)
    async def docs():
        return HTMLResponse(
            '<!doctype html><html lang="en"><meta charset="utf-8">'
            "<title>Resume Builder API</title><h1>Resume Builder API</h1>"
            '<p><a href="/openapi.json">OpenAPI contract</a></p>'
            "<ul><li>GET /api/health</li><li>POST /api/session/bootstrap</li>"
            "<li>POST /api/diagnostics</li><li>GET /api/diagnostics/latest</li></ul></html>"
        )

    original_openapi = app.openapi

    def session_openapi():
        document = original_openapi()
        document.setdefault("components", {}).setdefault("securitySchemes", {})["LocalSession"] = {
            "type": "apiKey",
            "in": "cookie",
            "name": COOKIE_NAME,
        }
        return document

    app.openapi = session_openapi

    @app.post(
        "/api/session/bootstrap", response_model=BootstrapResponse, operation_id="bootstrap_session"
    )
    async def bootstrap(body: BootstrapRequest, request: Request):
        session = sessions.redeem(body.ticket)
        if session is None:
            return error_response(401, request.state.request_id)
        response = JSONResponse({"authorized": True})
        response.set_cookie(COOKIE_NAME, session, httponly=True, samesite="strict", path="/")
        structlog.get_logger().info("session_started")
        return response

    @app.post(
        "/api/diagnostics",
        response_model=DiagnosticResponse,
        status_code=202,
        responses={200: {"model": DiagnosticResponse}},
        operation_id="create_diagnostic",
        openapi_extra=SESSION_SECURITY,
    )
    async def create_diagnostic(body: DiagnosticCreate, request: Request):
        try:
            outcome = await asyncio.to_thread(
                app.state.service.create,
                body.idempotency_key,
                request.state.principal,
                request_id=UUID(request.state.request_id),
            )
        except ActiveDiagnosticConflict:
            return error_response(409, request.state.request_id)
        structlog.get_logger().info(
            "diagnostic_created",
            request_id=request.state.request_id,
            execution_id=outcome.execution.id,
            status=outcome.execution.status,
            attempt_count=outcome.execution.attempt_count,
        )
        return JSONResponse(
            DiagnosticResponse(execution=outcome.execution).model_dump(mode="json"),
            status_code=202 if outcome.created else 200,
        )

    @app.get(
        "/api/diagnostics/latest",
        response_model=DiagnosticResponse,
        operation_id="get_latest_diagnostic",
        openapi_extra=SESSION_SECURITY,
    )
    async def latest_diagnostic(request: Request):
        return await asyncio.to_thread(app.state.service.latest, request.state.principal)

    if web_root is not None:
        directory = Path(web_root).resolve(strict=True)
        app.mount("/assets", StaticFiles(directory=directory / "assets"), name="assets")

        @app.get("/", include_in_schema=False, response_class=FileResponse)
        async def web_index():
            return FileResponse(directory / "index.html")

    return app
