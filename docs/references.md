# Referências técnicas oficiais

**Objetivo:** fontes para validar APIs, compatibilidade e práticas antes de codificar. Esta lista **não é um lockfile nem confirmação de versão instalada**. Fixar versões testadas nos projetos de implementação e registrar resultados do spike MCP.

## Backend Python e dados

- [FastAPI](https://fastapi.tiangolo.com/) — documentação oficial, OpenAPI e segurança.
- [Pydantic](https://docs.pydantic.dev/latest/) — validação, aliases, JSON Schema.
- [SQLAlchemy 2.x](https://docs.sqlalchemy.org/en/20/) — ORM e transações. Fixar série 2.x compatível testada; não migrar major/minor silenciosamente.
- [Alembic](https://alembic.sqlalchemy.org/en/latest/) — migrações.
- [SQLite](https://www.sqlite.org/docs.html), [WAL](https://sqlite.org/wal.html), [FTS5](https://sqlite.org/fts5.html) — limites de concorrência e busca.
- [uv](https://docs.astral.sh/uv/) — Python/dep/workspaces/lockfiles.
- [Dramatiq](https://dramatiq.io/) — workers, Redis, retries, async jobs.
- [Redis](https://redis.io/docs/latest/) — broker e configurações operacionais.
- [structlog](https://www.structlog.org/en/stable/) — logging estruturado.
- [Pytest](https://docs.pytest.org/en/stable/) — backend testes.

## Frontend e desktop

- [React](https://react.dev/), [TypeScript](https://www.typescriptlang.org/docs/), [Vite](https://vite.dev/).
- [pnpm Workspaces](https://pnpm.io/workspaces), [just](https://just.systems/man/en/), [Tauri](https://tauri.app/).
- [Vitest](https://vitest.dev/), [Playwright Test](https://playwright.dev/docs/intro).
- [Playwright Python](https://playwright.dev/python/) — **PDF e testes**, não submissão de vagas.
- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html) — contrato Python→TypeScript.

## MCP, IA, documentos e operação

- [Model Context Protocol](https://modelcontextprotocol.io/), [Python SDK](https://py.sdk.modelcontextprotocol.io/) — transportes/Tools/Resources/Prompts (checar versão SDK v2 e compatibilidade no M0.5).
- [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/), [Jaeger](https://www.jaegertracing.io/docs/), [Sentry Python](https://docs.sentry.io/platforms/python/).
- [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/), [python-docx](https://python-docx.readthedocs.io/en/latest/) — processamento e DOCX sob validação, não dependências escolhidas por ADR definitivo.
- [Freedesktop XDG Base Directory](https://specifications.freedesktop.org/basedir-spec/latest/), [Secret Service API](https://specifications.freedesktop.org/secret-service/latest/) — diretórios e keyring.

## Observações de validação

- Pacote de docs preparado em **2026-11-11**; todas as URLs devem ser rechecadas durante a implementação, e versões seguras compatíveis devem ser pinadas com `uv.lock` e lockfile pnpm.
- Não inferir compatibilidade de Hermes/Codex/Claude/Kimi com SDK Python apenas pela especificação: executar testes concretos.
- Fonts e ferramentas de design usadas como referência podem ter licenças: não redistribuir arquivos de fonte privada/embutida sem autorização; a recriação usa fallbacks.
