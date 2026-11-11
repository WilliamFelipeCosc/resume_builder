# STATE

## Decisions

Sem novas decisões globais. ADRs 001–015 existentes continuam vigentes; escolhas do diagnóstico M0 são locais à feature.

## Handoff

- **Feature**: m0-foundation
- **Phase / Task**: Phase 1 concluída / T7 próxima; execução autorizada em quatro lotes sequenciais
- **Completed**: T1 96de988; T2 abcc19a; T3 eb98ab8; T4 1640db8; T5 10084be; T6 neste commit. Gates: 81 Pytest, 3 Vitest, 1 Chromium headless; build/typecheck/locks/Ruff verdes
- **In-progress**: nenhum; batch 1 concluído
- **Next step**: batch 2 T7–T12, migração/repositório/posse/reconciliação/serviço/logs
- **Blockers**: nenhum. Bootstrap isolado comprovado; launcher desktop e autenticação definitiva ainda pendentes
- **Uncommitted files**: mudanças T6 no commit; .serena/ preexistente fora do escopo
- **Branch**: main

Módulos: `resume_core.paths.resolve_paths(environment, environ, test_root=...)` → EnvironmentPaths com create() explícito. `resume_core.contracts`: DiagnosticCreate (JSON somente idempotencyKey), DiagnosticExecution, DiagnosticResult, DeliveryWarning, DiagnosticError.for_code(), DiagnosticResponse. DTOs frozen/extra forbid, camelCase dump padrão, UUIDs, UTC normalizado, contador int estrito. API/Worker ainda pacotes vazios. Error codes/messages constantes no contrato; warning queue_unavailable.

Comandos: `.venv/bin/pytest tests/unit tests/integration tests/smoke -q` requer sockets fora do sandbox; `.venv/bin/ruff check backend tests tools`; `.venv/bin/ruff format --check backend tests tools`; `uv sync --all-packages --locked`; `pnpm --filter web test/typecheck/build` (cada script separadamente). uv/pnpm exigem cache externo autorizado. Chromium de teste em `/tmp/resume-builder-playwright`: `PLAYWRIGHT_BROWSERS_PATH=/tmp/resume-builder-playwright node apps/web/node_modules/@playwright/test/cli.js test --config apps/web/playwright.probe.config.ts`. Sem Redis, provider, CI, MCP ou dados privados usados. Guias: docs/engineering/m0-toolchain.md e tools/bootstrap_probe/README.md.
