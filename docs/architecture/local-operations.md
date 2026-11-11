# Execução local, filas, empacotamento e recuperação

## Stack aprovada

- Linux local-first; React/Vite TypeScript por pnpm; FastAPI Python por uv.
- Monólito modular + worker Dramatiq/Redis; `justfile` previsto para orquestração. RabbitMQ é perfil experimental opcional, jamais requisito.
- SQLite/SQLAlchemy 2/Alembic; banco em WAL; um escritor por vez, migrações controladas.
- MCP `stdio` primeiro, HTTP seguro em loopback até V1; Tauri/RPM em M7.

## Estrutura XDG sugerida

- Config: `${XDG_CONFIG_HOME:-~/.config}/resume-builder/`.
- Data: `${XDG_DATA_HOME:-~/.local/share}/resume-builder/` (`app.sqlite3`, docs e exports privados).
- Cache: `${XDG_CACHE_HOME:-~/.cache}/resume-builder/`.
- State: `${XDG_STATE_HOME:-~/.local/state}/resume-builder/` (logs sanitizados, auditoria permanece no banco).

Não colocar arquivos do usuário em `data/seeds/` versionado nem empacotar `private/` em releases.

## M0: requisitos operacionais mínimos

Diagnóstico health, worker job de teste, migração Alembic demonstrada, Redis em Compose iniciado manualmente (não instalador automático), circuito de falha de provider, bootstrap de logs seguros. Gerenciadores `pnpm` e `uv` distintos; não criar `uv.lock` antes de resolver dependências. Configurar versão/ambiente Python compatível ao SDK MCP verificado no spike.

## Worker e durabilidade

Dramatiq enfileira trabalho, SQLite é a fonte de verdade de progresso/resultados; Redis não garante por si só transações com banco. Registrar primeiro intenção do job com ID idempotente e reconciliar retries. Não iniciar processamento de documento com bytes arbitrários vindos do MCP.

## Backup/restore (M7, pré-requisitos antes)

Gerar snapshot SQLite consistente, sincronizar manifestos/arquivos com hash, testar restore em diretório temporário, validar migrações e links. Backup não inclui keyring, cookies, perfis Chrome ou Redis cache. `resume-agent doctor` diagnostica, nunca instala ou modifica dependências automaticamente.

## Entrega desktop

Tauri somente depois de Web estável, com processo Python local e suas dependências devidamente empacotadas/verificadas no Linux alvo. RPM obrigatório V1; AppImage opcional. Escolhas de empacotamento e permissões ainda abertas (`docs/decisions/open-decisions.md`).
