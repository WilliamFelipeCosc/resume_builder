# Estado do bootstrap — 2026-11-11

O repositório foi inicializado documentalmente em 04/11 e sincronizado com o pacote aprovado de 11/11 por solicitação do proprietário. A fonte atual é [PROJECT_SOURCE.md](../PROJECT_SOURCE.md); detalhes da importação, decisões e exclusões estão em [specification-sync-2026-11-11.md](specification-sync-2026-11-11.md).

M0 está em planejamento. Não há aplicação implementada, dependências instaladas, testes de produto executados ou compatibilidade MCP validada por esta sincronização. A entrevista define uma operação fictícia completa com dados fixos e recuperação controlada; implementação não iniciada.

A stack antiga foi substituída por React/Vite, FastAPI/Python, SQLite/SQLAlchemy 2/Alembic, Redis/Dramatiq, pnpm + uv + justfile. Gates M0: AC-M0-001/002; Reactive Resume passa a atividade opcional posterior.

O [registro de inicialização original](history/project-bootstrap-2026-11-04.md) é histórico. O manifesto original está em `docs/history/`; `MANIFEST.sha256` na raiz verifica os documentos e referências públicos atuais. Repositório público não implica licença de software; escolha de licença continua pendente.

Próximo passo: fechar escopo, contratos e testes de M0 com o proprietário. A prioridade continua M3, sobretudo construção e exportação do currículo; M0.5 mantém seu gate separado.
