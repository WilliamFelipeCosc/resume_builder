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

- **Feature**: m05-mcp-feasibility — contexto e especificação aprovados em 2026-11-12
- **Phase / Task**: M0.5 T1–T20 concluídas; verificação independente PASS com exceção histórica aceita pelo proprietário.
- **Completed**: Hermes e Codex validaram as duas tools e replay; proprietário conferiu os quatro campos sem envio. Correções de autorização, validação wire, framing e ambiente restrito commitadas; evidência e exceção em 905b720 e 93739b6.
- **Gates**: just check PASS: 431 testes Python, 17 Vitest, 3 Chromium, contratos, build e lint; just check-mcp-spike: 177 testes; validate_state PASS. Dois avisos de depreciação SDK.
- **Sensor**: revalidação independente detectou 5/5 mutações em cópia isolada; parecer anterior detectou 7/7.
- **In-progress**: nenhum desenvolvimento M0.5 pendente; relatório independente e lições registram a revalidação.
- **Next step**: seguir o roadmap, preservando o limite de investigação de 60 minutos; consultar validation.md e historical-exception.md para limites do aceite.
- **Blockers**: SPIKE-17 histórico não comprovado; proprietário aceitou exceção documentada em 2026-11-16. Continuidade exata do PID Hermes não medida durante chamadas.
- **Uncommitted files**: planejamento .specs/features/m05-mcp-feasibility/, STATE, ADR-016 e sincronização da escolha FastMCP em PROJECT_SOURCE/módulo/contratos/decisões; .serena/ preexistente permanece fora do escopo
- **Branch**: main

Operação: docs/engineering/m0-local-operation.md; just setup, just build, just redis-up (manual), just migrate, just api, just worker e just open. XDG_RUNTIME_DIR privado obrigatório; dados profissionais/providers/MCP/CI não utilizados. Testes: PLAYWRIGHT_BROWSERS_PATH=/tmp/resume-builder-playwright just check, Docker e Chromium necessários. Evidências detalhadas e limites em .specs/features/m0-foundation/validation.md.
