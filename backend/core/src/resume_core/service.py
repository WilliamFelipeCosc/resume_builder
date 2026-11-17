"""Authorized application boundary, shared by HTTP and future adapters."""

from dataclasses import dataclass
from enum import IntEnum
from uuid import UUID, uuid4

from resume_core.contracts import DiagnosticResponse
from resume_core.repository import CreateOutcome, DiagnosticRepository


class Clearance(IntEnum):
    PUBLIC = 0
    PROFESSIONAL = 1
    CONFIDENTIAL = 2
    SECRET = 3

    @classmethod
    def parse(cls, value: str) -> "Clearance":
        return cls[value.upper()]


@dataclass(frozen=True)
class Principal:
    subject: str
    capabilities: frozenset[str]
    clearance: Clearance = Clearance.PUBLIC


class PermissionDenied(Exception):
    pass


def require(principal: Principal | None, capability: str) -> None:
    if principal is None or not principal.subject or capability not in principal.capabilities:
        raise PermissionDenied("Diagnostic access denied")


class DiagnosticService:
    def __init__(self, repository: DiagnosticRepository):
        self.repository = repository

    def create(
        self, key: UUID, principal: Principal | None, *, request_id: UUID | None = None
    ) -> CreateOutcome:
        require(principal, "diagnostic:write")
        self.repository.reconcile()
        return self.repository.create(key, request_id or uuid4())

    def latest(self, principal: Principal | None) -> DiagnosticResponse:
        require(principal, "diagnostic:read")
        self.repository.reconcile()
        return DiagnosticResponse(execution=self.repository.latest())
