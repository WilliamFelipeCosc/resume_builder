# STATE

## Decisions

Sem novas decisões globais. ADRs 001–015 existentes continuam vigentes; escolhas do diagnóstico M0 são locais à feature.

## Handoff

- **Feature**: m0-foundation — concluída para AC-M0-001/002
- **Phase / Task**: T1–T22 concluídas; Verifier independente PASS em validation.md
- **Completed**: quatro lotes sequenciais, commits 96de988…f35b4e0; 23/23 FNDs verificados
- **Gates**: just setup locked e just check independentes: 254 Pytest, 17 Vitest, 3 Chromium, tipos/Vite/geração determinística/Ruff; Compose e manifesto verificados; validate_state.py sem erros
- **Sensor**: oito mutações de auth/prazo/posse/idempotência/integridade detectadas em scratch; nenhuma sobreviveu; nenhuma mudança real de código/testes pelo Verifier
- **In-progress**: nenhum
- **Next step**: tarefa M0 concluída; aguardar escolha do próximo marco. M0.5 tem gate próprio e ainda não começou
- **Blockers**: nenhum para os testes automatizados M0. Navegador desktop padrão não aberto manualmente; Chromium headless validado. Warnings Starlette/HTTPX e cores documentados
- **Uncommitted files**: fechamento documental/manifesto neste commit; .serena/ preexistente permanece fora do escopo
- **Branch**: main

Operação: docs/engineering/m0-local-operation.md; just setup, just build, just redis-up (manual), just migrate, just api, just worker e just open. XDG_RUNTIME_DIR privado obrigatório; dados profissionais/providers/MCP/CI não utilizados. Testes: PLAYWRIGHT_BROWSERS_PATH=/tmp/resume-builder-playwright just check, Docker e Chromium necessários. Evidências detalhadas e limites em .specs/features/m0-foundation/validation.md.
