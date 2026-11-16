# STATE

## Decisions

ADRs 001–015 existentes continuam vigentes; escolhas do diagnóstico M0 são locais
à feature. A escolha FastMCP aprovada no M0.5 está registrada em AD-001/ADR-016.

### AD-001
- **Decision**: Usar FastMCP independente como adapter MCP, chamando Application Services Python compartilháveis; stdio no M0.5 e integração HTTP com FastAPI no M4.
- **Reason**: Escolha explícita do proprietário e desenho consolidado aprovado; manter o spike independente da API e preservar evolução para HTTP.
- **Trade-off**: Dependências adicionais do framework e concessão local própria no processo stdio, em lugar de mediação REST interna.
- **Scope**: MCP e integração futura com FastAPI; ADR-016 complementa ADRs 004/005 sem alterar seus limites.
- **Date**: 2026-11-12
- **Status**: active

## Handoff

- **Feature**: harness-status — reconciliação de 31 slices, status canônico, verificação de divergência e modelo de medição.
- **Phase / Task**: T1–T4 concluídas; parecer independente PASS com limitações em `.specs/features/harness-status/validation.md`.
- **Completed**: registro canônico `docs/process/milestone-status.json`; notas Obsidian M0–M7 e índice sincronizados; checker de snapshot offline; modelo de medição preparado para M1.
- **Gates**: 4 testes focais, Ruff check e format, snapshot real e validate_state passaram. Sensor independente detectou 2/2 mutações; `just check` completo não foi executado nesta alteração de processo.
- **In-progress**: piloto e retrospectiva M1 dependem de autorização e execução posteriores; não são alegados como concluídos.
- **Next step**: preparar M1 conforme AC-M1-001/002/003 e usar `docs/process/milestone-effort-template.md`; consultar `docs/process/milestone-status-workflow.md` antes de atualizar estados.
- **Blockers**: tempo ativo histórico SPIKE-17 não comprovado; exceção aceita em M0.5. O checker não mede disponibilidade nem texto narrativo do vault em tempo real.
- **Uncommitted files**: alterações preexistentes em PROJECT_SOURCE, ADR-016, contratos/módulos/decisões, contexto/pesquisa M0.5 e `.serena/` continuam fora do escopo.
- **Branch**: main

Operação: docs/engineering/m0-local-operation.md; just setup, just build, just redis-up (manual), just migrate, just api, just worker e just open. XDG_RUNTIME_DIR privado obrigatório; dados profissionais/providers/MCP/CI não utilizados. Testes: PLAYWRIGHT_BROWSERS_PATH=/tmp/resume-builder-playwright just check, Docker e Chromium necessários. Evidências detalhadas e limites em .specs/features/m0-foundation/validation.md.
