"""FND-14: authorization must precede every read, write or reconciliation."""

from uuid import uuid4

import pytest
from resume_core.service import DiagnosticService, PermissionDenied, Principal


class RepositorySpy:
    def __init__(self):
        self.calls = []

    def reconcile(self):
        self.calls.append("reconcile")

    def create(self, *args):
        self.calls.append("create")

    def latest(self):
        self.calls.append("latest")


@pytest.mark.parametrize(
    "principal",
    [
        None,
        Principal("", frozenset({"diagnostic:read", "diagnostic:write"})),
        Principal("linux-user", frozenset()),
    ],
)
@pytest.mark.parametrize("operation", ["create", "latest"])
def test_unauthorized_service_has_zero_repository_access(principal, operation):
    spy = RepositorySpy()
    service = DiagnosticService(spy)
    with pytest.raises(PermissionDenied, match="Diagnostic access denied"):
        if operation == "create":
            service.create(uuid4(), principal)
        else:
            service.latest(principal)
    assert spy.calls == []


def test_read_only_principal_cannot_create():
    spy = RepositorySpy()
    service = DiagnosticService(spy)
    with pytest.raises(PermissionDenied):
        service.create(uuid4(), Principal("reader", frozenset({"diagnostic:read"})))
    assert spy.calls == []


def test_write_only_principal_cannot_read():
    spy = RepositorySpy()
    service = DiagnosticService(spy)
    with pytest.raises(PermissionDenied):
        service.latest(Principal("writer", frozenset({"diagnostic:write"})))
    assert spy.calls == []
