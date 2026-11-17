"""Concrete typed career routes backed by authorized application services."""

import asyncio
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from resume_core.career_kb.contracts import CREATE_TYPES, READ_TYPES, Page
from resume_core.career_kb.create import InvalidEvidence, ReferenceNotFound
from resume_core.career_kb.queries import ListQuery, ResponseTooLarge
from resume_core.career_kb.repository import ReceiptConflict
from resume_core.persistence.unit_of_work import DatabaseBusy
from resume_core.service import PermissionDenied

from resume_api.errors import error_response

router = APIRouter()
SECURITY = {"security": [{"LocalSession": []}]}


class CareerCreated(BaseModel):
    id: UUID
    revisionId: UUID


def register_routes(kind):
    async def create(body, request: Request):
        try:
            result, created = await asyncio.to_thread(
                request.app.state.career_create.create,
                request.state.principal,
                kind,
                body,
                request_id=request.state.request_id,
            )
        except PermissionDenied:
            return error_response(403, request.state.request_id, code="forbidden")
        except ReferenceNotFound:
            return error_response(404, request.state.request_id)
        except ReceiptConflict:
            return error_response(409, request.state.request_id, code="idempotency_conflict")
        except InvalidEvidence:
            return error_response(422, request.state.request_id)
        except DatabaseBusy:
            return error_response(503, request.state.request_id, code="database_busy")
        return JSONResponse(result, status_code=201 if created else 200)

    create.__annotations__["body"] = CREATE_TYPES[kind]
    router.add_api_route(
        f"/api/career/{kind}",
        create,
        methods=["POST"],
        response_model=CareerCreated,
        status_code=201,
        responses={200: {"model": CareerCreated}},
        operation_id=f"create_{kind}",
        openapi_extra=SECURITY,
    )

    async def list_items(
        request: Request,
        offset: int = Query(0, ge=0, le=10000),
        limit: int = Query(25, ge=1, le=100),
        sort: Literal["createdAt", "-createdAt"] = "createdAt",
        archived: bool | None = None,
        confirmation: Literal["confirmed", "unverified"] | None = None,
        confirmation_field: Literal[
            "fullName",
            "professionalHeadline",
            "email",
            "phoneOriginal",
            "objectiveOriginal",
            "cityOfResidence",
            "countryOfResidence",
            "linkedinUrl",
            "githubUrl",
        ]
        | None = Query(None, alias="confirmationField"),
    ):
        try:
            query = ListQuery(
                offset=offset,
                limit=limit,
                sort=sort,
                archived=archived,
                confirmation=confirmation,
                confirmationField=confirmation_field,
            )
            return await asyncio.to_thread(
                request.app.state.career_queries.list, request.state.principal, kind, query
            )
        except PermissionDenied:
            return error_response(403, request.state.request_id, code="forbidden")
        except ValueError:
            return error_response(422, request.state.request_id)
        except ResponseTooLarge:
            return error_response(422, request.state.request_id, code="response_too_large")

    router.add_api_route(
        f"/api/career/{kind}",
        list_items,
        methods=["GET"],
        response_model=Page[READ_TYPES[kind]],
        operation_id=f"list_{kind}",
        openapi_extra=SECURITY,
    )

    async def detail(entity_id: UUID, request: Request):
        try:
            result = await asyncio.to_thread(
                request.app.state.career_queries.detail, request.state.principal, kind, entity_id
            )
        except PermissionDenied:
            return error_response(403, request.state.request_id, code="forbidden")
        except ResponseTooLarge:
            return error_response(422, request.state.request_id, code="response_too_large")
        if result is None:
            return error_response(404, request.state.request_id)
        return result

    router.add_api_route(
        f"/api/career/{kind}/{{entity_id}}",
        detail,
        methods=["GET"],
        response_model=READ_TYPES[kind],
        operation_id=f"get_{kind}",
        openapi_extra=SECURITY,
    )


for career_kind in CREATE_TYPES:
    register_routes(career_kind)
