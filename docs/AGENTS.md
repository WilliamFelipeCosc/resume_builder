# Documentação modular

Escopo: `docs/**`. Comandos partem da raiz.

- Use `docs/README.md` e ADR-013 para autoridade/precedência. Requisitos aprovados não podem desaparecer por simplificação editorial; propostas e decisões OPEN devem permanecer identificadas.
- Separe requisito, implementação, verificação independente e aceite humano. Estado canônico dos marcos: `docs/process/milestone-status.json`; evidências detalhadas: `.specs/`.
- Documente novas decisões sem reescrever silenciosamente decisões anteriores. Mudança de comportamento/arquitetura exige sincronizar módulo, contrato e ADR afetados.
- Registros em `docs/history/`, `package-import-2026-11-11.json` e `specification-sync-2026-11-11.md` são históricos; preserve hashes/afirmações com seu contexto temporal. Não transformar histórico em instrução ativa.
- Mantenha `PROJECT_OVERVIEW.md` breve, com links para detalhes; os documentos completos arquivados não são dependência de clone/build/CI.
- Sincronize notas afetadas no Obsidian pelo MCP com leitura prévia e controle de versão; siga `docs/process/milestone-status-workflow.md`. Não copiar fontes privadas para o vault.
- Confira links/caminhos e `git diff --check`. Se alterar arquivos cobertos por `MANIFEST.sha256`, atualize o manifesto da árvore atual; não alterar manifestos históricos. Mudança só documental não exige a suíte da aplicação.
