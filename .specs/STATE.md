# STATE

## Decisions

Sem novas decisões globais. ADRs 001–015 existentes continuam vigentes; escolhas do diagnóstico M0 são locais à feature.

## Handoff

- **Feature**: m0-foundation
- **Phase / Task**: T1–T22 implementadas; validação independente obrigatória pendente
- **Completed**: T19 ca32496; T20 84f3568; T21 dea9a0e; T22 neste commit; T1–T18 até b7627c0
- **Gates**: `just setup` locked; `PLAYWRIGHT_BROWSERS_PATH=/tmp/resume-builder-playwright just check`: 254 Pytest,17 Vitest,1 Chromium probe+2 definitivos; TS/Vite, duas gerações temporárias idênticas, Ruff/format/diff verdes; Compose config validado
- **In-progress**: nenhum worker; root deve despachar Verifier novo antes de declarar M0 completo
- **Next step**: Verifier rederiva FND-01…23/AC-M0-001/002, roda gates e ≥5 mutações de auth/integridade em scratch; escreve validation.md e root roda validate_state.py. Atualizar manifesto após relatório/status finais
- **Blockers**: nenhum. Navegador desktop padrão não aberto; Chromium158 headless comprovado. Warnings Starlette/HTTPX e cores permanecem; M0.5/provider/CI/privados não usados
- **Uncommitted files**: T22 no commit; somente .serena/ preexistente fora do escopo depois dele
- **Branch**: main

Operação: `just setup`, `just build`, Redis manual `just redis-up`, `just migrate`, `just api`, `just worker`, `just open`; encerrar serviços e `just redis-down`. Guia docs/engineering/m0-local-operation.md. CLI `.venv/bin/python -m resume_api [--environment test --test-root /tmp/<raiz>] migrate|serve|worker|open`; XDG_RUNTIME_DIR privado exigido. Serve recusa DB ausente, host127.0.0.1, porta8000; testes8031. Sem migrations/Redis implícitos. LogsJSONstderr; launcher xdg-open descarta streams e nunca imprime ticket.

Checks: `just check` exige Docker+Chromium; pytest basetemp curto `/tmp/rb-tests` por AF_UNIX108bytes. Harness Redis fixa `redis@sha256:71885d8cc6e42f2bc0aa2eb853bfc4be200b5108a46ac50e117ae1df0531fb80`, somente containers próprios loopback/sem persistência. tools/web_harness executa CLI real com dados temporários e subprocessos; restart SIGHUP existe somente no harness. tests/integration/controlled_worker.py contém fault injection e clockfile atômico, não API pública.

Contrato: `just generate` exporta offline+geraSDK, `just check-contract` compara em /tmp sem alterar artefatos reais. Gerador HeyAPI0.99 usa TS6.0.3 local (TS7 removeu SyntaxKind clássico); frontendTS7 preservado. SDK em packages/api-client/src/generated; consumidor React usa somente DTOs gerados.
