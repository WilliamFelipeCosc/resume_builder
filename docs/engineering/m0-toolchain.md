# Toolchain do M0

Decisão técnica T1, 2026-11-11. Escopo: FND-20/21/23, AC-M0-001/002.

## Ambiente e compatibilidade declarada

Comandos executados localmente: `python3 --version`, `uv --version`, `node --version`, `pnpm --version`, `just --version`, `docker --version`, `docker compose version` e `python3 -c 'import sqlite3; print(sqlite3.sqlite_version)'`.

| Ferramenta | Observada / selecionada |
|---|---|
| Python | 3.14.8, projeto >=3.14,<3.15 |
| uv | 0.12.7 |
| Node | 24.18.0, projeto >=24.18,<25 |
| pnpm | 11.28.9, packageManager fixo |
| just | 1.57.0 |
| Docker / Compose | 29.8.2 / 5.6.0; daemon ainda não validado |
| SQLite Python | 3.51.2 |

Metadados oficiais consultados em 2026-11-11 via JSON PyPI/npm. Versões selecionadas para os próximos manifests: FastAPI 0.162.4, Pydantic 2.14.3, SQLAlchemy 2.1.8, Alembic 1.20.1, Dramatiq 2.2.1, redis-py 8.1.0, structlog 26.1.0, Uvicorn 0.54.0; Pytest 9.2.0, HTTPX 0.28.1, Ruff 0.17.4 e uv_build 0.13.7. Todos declaram um mínimo Python compatível com 3.14; isso não comprova integração. T2 verifica resolução, instalação e imports reais antes de concluir compatibilidade.

Frontend: React 19.3.1, Vite 8.3.8, plugin-react 6.3.0, Vitest 5.1.0, TypeScript 7.0.2, Playwright Test 1.65.0 e Hey API 0.99.0. Node 24.18 atende engines publicados de Vite/plugin (>=22.12), Vitest (^24), TypeScript (>=16.20), Playwright (>=20) e Hey API (>=22.18). T3 verifica peer dependencies, lock, testes e build reais. Locks são a fonte exata das dependências transitivas.

Fontes: [PyPI](https://pypi.org/), [registry npm](https://registry.npmjs.org/), [uv workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces/), [Vite](https://vite.dev/guide/), [Vitest](https://vitest.dev/guide/).

## Gerador OpenAPI → TypeScript

Selecionado `@hey-api/openapi-ts` 0.99.0, com plugins TypeScript, SDK e Fetch. Entrada é arquivo OpenAPI exportado offline da FastAPI; geração local, sem upload de schema. [Configuração oficial](https://heyapi.dev/docs/openapi/typescript/get-started).

| Alternativa | Tradeoff |
|---|---|
| Hey API | Gera tipos e chamadas, atende T19 sem funções HTTP manuais; configuração/plugins precisam ficar pinados |
| openapi-typescript + openapi-fetch | Boa opção leve, mas tipos e transporte separados exigem composição de chamadas; menor ganho neste contrato pequeno |
| OpenAPI Generator | Gera SDK completo, mas adiciona runtime/toolchain de geração desnecessários ao M0 |

Não adicionar biblioteca de UI, autenticação, scheduler ou estado remoto. Ruff cobre lint/format Python; TypeScript strict cobre o contrato e frontend; Vitest cobre comportamento e Playwright Test roda fora da aplicação. Testes usam somente dados sintéticos. Essas escolhas de tooling não resolvem OPEN-01…07.

## Comandos previstos e gates

Em T2: `uv sync --all-packages --locked`, `uv run pytest tests/smoke -q`, `uv run ruff check backend tests` e `uv run ruff format --check backend tests`. Root virtual inclui core/API/Worker; não antecipar MCP.

Em T3: `pnpm install --frozen-lockfile`, `pnpm --filter web test`, `pnpm --filter web typecheck`, `pnpm --filter web build`. Cliente vazio até T19; nenhum DTO manual.

Em T4: integração Python e navegador Chromium real com diretórios temporários; comprovar SO_PEERCRED, ticket único/TTL, cookie, fragmento, restart e logs. Falha bloqueia avanço, sem fallback.

Redis será iniciado manualmente pelo operador em T22. Nenhum comando desta nota instala ferramenta de sistema, inicia Docker/Redis ou provider. Dependências do projeto ficam em `.venv` e `node_modules`; checks usam bancos/diretórios temporários. Não consultar `private/`.

## Evidências de T1

Três checks documentais concluídos: (1) versões das nove ferramentas verificadas; (2) mínimos Python/engines Node comparados aos metadados oficiais; (3) escolha de gerador e comandos conferidos contra contrato, desenho e documentação oficial. `validate_spec.py m0-foundation`, `validate_tasks.py m0-foundation` e `git diff --check` passam. Nenhum teste de runtime é alegado por T1; locks, execução integrada e compatibilidade real permanecem pendentes.

## Compatibilidade comprovada em T19

A geração real com Hey API 0.99.0 falhou com TypeScript 7.0.2: `ts.SyntaxKind` não está mais na exportação principal. O peer range publicado aceita 7, mas o gerador usa a API clássica do compilador. Fixado TypeScript **6.0.3 somente no pacote api-client**, consultado no registry oficial (`pnpm view typescript@6 version --json`). O frontend conserva TypeScript 7.0.2. Esta é uma correção de compatibilidade de tooling, sem mudar contratos ou OPENs.

Comandos executados: `.venv/bin/python -m resume_api.export_openapi --output packages/api-client/openapi.json`; `pnpm --filter @resume-builder/api-client generate`; geração repetida com hashes dos 16 arquivos idênticos; `pnpm --filter web typecheck` compila consumidor e request negativo em `apps/web/tests/client-contract.ts`. Entrada/saída são arquivos locais, sem upload do schema. Docs HTML locais sem CDN e OpenAPI HTTP exigem cookie; health retorna somente status.

T19: 237 Pytest (5 novos), 3 Vitest e 1 Chromium probe passaram; Ruff/format e build/typecheck verdes. O executável pnpm no sandbox reporta Node embutido 26, enquanto seus scripts usam Node 24.18; a instalação frozen foi validada no ambiente autorizado, sem esse aviso. O warning Starlette/HTTPX existente e o warning de cores Playwright permanecem registrados, sem testes ignorados.
