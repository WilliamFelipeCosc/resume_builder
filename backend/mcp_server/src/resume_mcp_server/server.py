"""Scoped MCP adapter for the synthetic application services."""

import json
from typing import Literal
from uuid import uuid4

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.middleware import Middleware
from pydantic import ValidationError
from resume_core.mcp_spike.contracts import (
    ApplicationContext,
    ContextQuery,
    Envelope,
    ErrorDetail,
    ErrorEnvelope,
    Policy,
    ProgressReport,
    Provenance,
    Receipt,
    check_json_size,
)
from resume_core.mcp_spike.policy import Profile
from resume_core.mcp_spike.repository import Conflict, TemporarilyUnavailable
from resume_core.mcp_spike.service import ContextNotFound, ContextService, ProgressService
from resume_core.service import PermissionDenied


def _error(code: str) -> ToolError:
    messages = {
        "SCHEMA_INVALID": "Invalid request.",
        "NOT_AUTHORIZED": "Access denied.",
        "CONTEXT_NOT_FOUND": "Context not found.",
        "CONFLICT": "Conflicting report.",
        "TEMPORARILY_UNAVAILABLE": "Temporarily unavailable.",
        "CONTEXT_TRUNCATED": "Context exceeds the output limit.",
        "INTERNAL_ERROR": "Internal error.",
    }
    payload = ErrorEnvelope(
        schemaVersion="m05.v1",
        error=ErrorDetail(code=code, message=messages[code]),
        requestId=str(uuid4()),
    )
    return ToolError(
        json.dumps(payload.model_dump(by_alias=True), ensure_ascii=False, separators=(",", ":"))
    )


class SafeToolMiddleware(Middleware):
    async def on_call_tool(self, context, call_next):
        name = context.message.name
        arguments = context.message.arguments or {}
        try:
            check_json_size(arguments, 4096)
            if name == "get_application_context":
                ContextQuery.model_validate(arguments)
            elif name == "report_application_progress":
                ProgressReport.model_validate(arguments)
            return await call_next(context)
        except ValidationError, ValueError:
            raise _error("SCHEMA_INVALID") from None
        except PermissionDenied:
            raise _error("NOT_AUTHORIZED") from None
        except ContextNotFound:
            raise _error("CONTEXT_NOT_FOUND") from None
        except Conflict:
            raise _error("CONFLICT") from None
        except TemporarilyUnavailable:
            raise _error("TEMPORARILY_UNAVAILABLE") from None
        except ToolError as exc:
            try:
                safe = ErrorEnvelope.model_validate_json(str(exc))
            except ValidationError, ValueError:
                raise _error("INTERNAL_ERROR") from None
            raise _error(safe.error.code) from None
        except Exception:
            raise _error("INTERNAL_ERROR") from None


def create_server(
    principal: Profile, contexts: ContextService, progress: ProgressService
) -> FastMCP:
    server = FastMCP(
        "m05-synthetic", middleware=[SafeToolMiddleware()], strict_input_validation=True
    )

    def invoke(callback):
        try:
            return callback()
        except PermissionDenied:
            raise _error("NOT_AUTHORIZED") from None
        except ContextNotFound:
            raise _error("CONTEXT_NOT_FOUND") from None
        except Conflict:
            raise _error("CONFLICT") from None
        except TemporarilyUnavailable:
            raise _error("TEMPORARILY_UNAVAILABLE") from None
        except Exception:
            raise _error("INTERNAL_ERROR") from None

    def envelope(data, application_id: str, provenance: list[Provenance]):
        try:
            return Envelope[
                ApplicationContext if isinstance(data, ApplicationContext) else Receipt
            ](
                schemaVersion="m05.v1",
                data=data,
                provenance=provenance,
                truncated=False,
                policy=Policy(
                    clientId=principal.client_id,
                    applicationId=application_id,
                    capabilities=list(principal.capabilities),
                ),
                requestId=str(uuid4()),
            ).model_dump(mode="json", by_alias=True)
        except ValidationError, ValueError:
            raise _error("CONTEXT_TRUNCATED") from None

    @server.tool
    def get_application_context(applicationId: str) -> dict:
        """Retrieve the authorized synthetic application context."""
        query = ContextQuery(applicationId=applicationId)
        data = invoke(lambda: contexts.get(principal, query))
        return envelope(
            data, applicationId, [Provenance(sourceId="synthetic-fixture", version="m05.v1")]
        )

    @server.tool
    def report_application_progress(
        applicationId: str,
        executionId: str,
        idempotencyKey: str,
        event: Literal["started", "form_filled", "blocked"],
    ) -> dict:
        """Record a reported progress event without confirming submission."""
        report = ProgressReport(
            applicationId=applicationId,
            executionId=executionId,
            idempotencyKey=idempotencyKey,
            event=event,
        )
        return envelope(invoke(lambda: progress.report(principal, report)), applicationId, [])

    return server
