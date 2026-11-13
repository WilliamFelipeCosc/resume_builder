# Evidência integrada M0.5

**Status: gates de execução passaram; verificação independente pendente.** Não
declarar o marco concluído antes do relatório independente e de `validate_state.py`.

O spike usa FastMCP 4.1.8 / MCP SDK 2.3.0, serviços Python locais e SQLite
exclusivo, com dados fictícios. Os relatos usam `reported_by_agent`, sem inferir
confirmação de envio. O transporte MCP HTTP permanece fora deste marco.

## Evidências de execução

- [Hermes real](live/hermes.md): descoberta, consulta, relato e replay.
- [Codex real](live/codex.md): descoberta, consulta, relato e replay.
- [Demonstração](live/form-demo.md): navegador da CLI, recibo e confirmação
  visual de cada campo e ausência de envio pelo proprietário.
- Gate anterior da fase 3: `just check-python`, 422 passed; `just check-mcp-spike`,
  168 passed; `just lint`, passou. Dois avisos de depreciação do SDK nos testes.
- Gate MCP repetido nesta fase: `just check-mcp-spike`, 168 passed e os mesmos
  dois avisos. `uv sync --all-packages --locked` passou (85 pacotes resolvidos,
  81 checados). `pnpm install --frozen-lockfile` passou com pnpm 11.28.9.
- Primeira tentativa de `just check` nesta fase: 422 testes Python passaram;
  gate interrompido em `check-web` porque `pnpm` não estava no PATH.
  `pnpm 11.28.9` instalado foi localizado.
- Reexecução de `just check` com PATH corrigido e
  `PLAYWRIGHT_BROWSERS_PATH=/tmp/resume-builder-playwright`: exit 0; 422 testes
  Python (dois avisos SDK), 17 Vitest, typecheck/build, compatibilidade
  OpenAPI/SDK, 3 testes Chromium e lint/formatação/diff check passaram.

## Mapa para verificação independente

Os caminhos abaixo são referências às evidências a inspecionar, não um parecer
independente de cobertura ou veredito de aceite. Todos os caminhos são relativos
à raiz do repositório.

| Requisito | Evidência a revisar |
| --- | --- |
| SPIKE-01 | `tests/integration/mcp_spike/test_stdio_adapter.py`; live/hermes.md; live/codex.md |
| SPIKE-02 | `tests/unit/mcp_spike/test_fixture.py`; `tests/unit/mcp_spike/test_context_service.py`; live/hermes.md; live/codex.md |
| SPIKE-03 | `tests/unit/mcp_spike/test_policy.py`; `tests/unit/mcp_spike/test_context_service.py` |
| SPIKE-04 | `tests/integration/mcp_spike/test_profiles.py`; `tests/integration/mcp_spike/test_mcp_spike_operations.py`; live/form-demo.md |
| SPIKE-05 | `tests/integration/mcp_spike/test_dependency_logging.py`; `tests/integration/mcp_spike/test_stdio_adapter.py` |
| SPIKE-06 | `tests/unit/mcp_spike/test_progress_service.py`; live/hermes.md; live/codex.md |
| SPIKE-07 | `tests/integration/mcp_spike/test_repository.py`; `tests/integration/mcp_spike/test_mcp_spike_operations.py` |
| SPIKE-08 | `tests/integration/mcp_spike/test_repository.py`; live/hermes.md; live/codex.md |
| SPIKE-09 | `tests/integration/mcp_spike/test_repository.py`; `tests/unit/mcp_spike/test_progress_service.py` |
| SPIKE-10 | `tests/unit/mcp_spike/test_policy.py`; `tests/unit/mcp_spike/test_progress_service.py` |
| SPIKE-11 | `tests/unit/mcp_spike/test_contracts.py`; `tests/integration/mcp_spike/test_database.py`; live/form-demo.md |
| SPIKE-12 | `tests/unit/mcp_spike/test_form_fixture.py`; live/form-demo.md |
| SPIKE-13 | `tests/integration/mcp_spike/test_form_server.py`; live/form-demo.md |
| SPIKE-14 | `tests/unit/mcp_spike/test_fixture.py`; live/form-demo.md |
| SPIKE-15 | `tests/unit/mcp_spike/test_progress_service.py`; live/form-demo.md |
| SPIKE-16 | `docs/engineering/m05-mcp-operation.md`; live/hermes.md; live/codex.md; live/form-demo.md |
| SPIKE-17 | `docs/engineering/m05-mcp-operation.md`; live/hermes.md; live/codex.md |
| SPIKE-18 | `tests/unit/mcp_spike/test_context_service.py`; `tests/unit/mcp_spike/test_progress_service.py`; `tests/integration/mcp_spike/test_stdio_adapter.py` |
| SPIKE-19 | `tests/unit/mcp_spike/test_contracts.py`; `tests/integration/mcp_spike/test_stdio_adapter.py` |
| SPIKE-20 | `tests/integration/mcp_spike/test_repository.py`; `tests/integration/mcp_spike/test_stdio_adapter.py` |
| SPIKE-21 | `tests/integration/mcp_spike/test_repository.py`; `tests/integration/mcp_spike/test_database.py` |

AC-M05-001 deve ser reavaliado com as evidências das duas CLIs e testes de
segurança; AC-M05-002 com a demonstração e a confirmação visual. O Verifier
deve validar resultados contra a spec e executar o sensor em scratch isolado.
