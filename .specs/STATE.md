# STATE

## Decisions

Sem novas decisões globais. ADRs 001–015 existentes continuam vigentes; escolhas do diagnóstico M0 são locais à feature.

## Handoff

- **Feature**: m0-foundation
- **Phase / Task**: Phase2 concluída / T13 próxima; quatro lotes sequenciais autorizados
- **Completed**: T1–T6 cf2cfe6; T7 be9e62a; T8 5cbe8fa; T9 6ffe4c8; T10 4a003b6; T11 39ecfc5; T12 neste commit. Gates157 Pytest,3 Vitest,1 Chromium; Ruff/typecheck/build/spec/tasks verdes
- **In-progress**: nenhum; batch2 concluído
- **Next step**: batch3 T13–T18, sessão Unix/HTTP/bootstrap/diagnóstico/Redis/Worker
- **Blockers**: nenhum; somente .serena/ preexistente fora do escopo. API/Worker ainda não integrados; Redis não iniciado
- **Branch**: main

Interfaces: `resume_core.database.make_engine(absolute_path)` SQLite WAL/busy_timeout250ms/hide_parameters; `migration_config(engine)` explicit Alembic `command.upgrade(...,"head")`; migration path backend/migrations, integer Unix microseconds UTC, JSON camelCase fixed/check constraints. No implicit migration in requests.

`DiagnosticRepository(engine,clock=aware_datetime_callable)` methods: `create(UUID key,UUID request_id)->CreateOutcome(execution,created)`, `latest()/get(UUID)->DiagnosticExecution|None`, `claim(UUID)->Lease(execution,token UUID,expires_at UTC)|None`, `complete(UUID,token)->bool`, `fail_attempt(UUID,token)->bool`, `reconcile()->int changes`. Atomic BEGIN IMMEDIATE writes, clock after lock; no broker/processing in transactions. claim only pending/queued,budget<3,total<120; lease min30/total. complete/fail require current valid token/time. Reconcile recovers expired lease sameID, third attempt/deadline terminal. No delivery adapter methods yet; T17 adds conditional publish acknowledgement/warning/next_delivery support.

`DiagnosticService(repo).create(key,principal,request_id=UUID|None)->CreateOutcome`; `.latest(principal)->DiagnosticResponse`. `Principal(subject, frozenset({"diagnostic:read","diagnostic:write"}))`; required capability before any repo call. API derives trusted principal only after valid session. Service reconciles before create/latest. Exceptions `PermissionDenied`, `ActiveDiagnosticConflict` need HTTP401/409 mapping.

`configure_logging(stream=None)` from resume_core.logging_policy: process-wide structlog+stdlib JSON allowlist to stderr. Call after dependencies load, no reconfiguration afterward: Uvicorn log_config=None, Dramatiq skip_logging. Event constants EVENTS; metadata request_id/execution_id UUIDs,status,attempt_count,stable code,method,route,status_code. Unknown raw event =>dependency_event; payloads,cookies,tickets,exceptions always dropped. No logger/stack/raw message fields; foreign handlers reset to safe root pipeline.

Commands: `.venv/bin/pytest tests/unit tests/integration tests/smoke -q` (requires actual sockets outside sandbox); `.venv/bin/ruff check backend tests tools`; `.venv/bin/ruff format --check backend tests tools`; Web `pnpm --filter web test`, `typecheck`, `build`. Browser `PLAYWRIGHT_BROWSERS_PATH=/tmp/resume-builder-playwright node apps/web/node_modules/@playwright/test/cli.js test --config apps/web/playwright.probe.config.ts` Chromium158 headless. uv/pnpm cache/network may require escalation; git writes need escalation. No private/provider/CI/MCP use. Contracts/paths from batch1 preserved; see spec/design/tasks and tools/bootstrap_probe/README.md.
