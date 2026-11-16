# Decisões de implementação em aberto — OPEN (não DECIDED)

Fonte: `PROJECT_SOURCE.md` §12. **Não alterar ADRs 001–015** sem aprovação explícita.

| ID provisório | Tema | Perguntas / validação para decisão | Quando |
|---|---|---|---|
| OPEN-01 | Nome/identidade do app | Nome público e UI branding (distintos do currículo) | Após M3 quando não bloquear |
| OPEN-02 | Editor e UI | Biblioteca inline/drag-and-drop, templates extras, componentes; perf e acessibilidade | M6 |
| OPEN-03 | Retrieval híbrido | Runtime/modelo embeddings local, armazenamento vetorial, fusão/rank e benchmarks | M6 |
| OPEN-04 | Compatibilidade MCP e auth HTTP | Spike stdio M0.5 validado com FastMCP 4.1.8/SDK 2.3.0, Hermes e Codex; transporte e autorização HTTP permanecem pendentes | M4 |
| OPEN-05 | Hermes provider | Viabilidade de chamada, credenciais, vision e limites reais; sem presumir grátis | Spike controlado antes de depender dele |
| OPEN-06 | AI Evals | Corpus e baselines para schema/precision/recall/latência/tokens/custo | Evolução M3–M7 |
| OPEN-07 | Tauri/RPM | Processo Python/Chromium, integração Linux, distribuição, permissões | M7 |

**Fechado, não reabrir aqui:** backend FastAPI/Python, SQLAlchemy 2/Alembic, Dramatiq/Redis, pnpm+uv+justfile, Pytest/structlog, MCP-first, template visual padrão e alternativa ATS, modelo KB ampliado, M3 prioritário.

Pequenas escolhas de implementação (por exemplo, nomes de rotas ou versões exatas) exigem spike/nota técnica; preferir ADR adicional se a decisão mudar comportamento ou riscos.
