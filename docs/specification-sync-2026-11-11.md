# Sincronização da especificação — 2026-11-11

## Decisões do proprietário

- Adotar o pacote aprovado em `/home/williamf/Documentos/Projects/resume_builder_spec/`, reconciliado com o Obsidian, e atualizar este repositório.
- Priorizar chegar a M3 rapidamente, sobretudo construção e exportação do currículo. Disponibilidade semanal sem limite definido por enquanto; nenhum prazo foi informado.
- Demonstrar M0 com uma operação fictícia completa: botão de diagnóstico com dados sintéticos fixos → API → SQLite → Worker → resultado persistido e visível na Web.
- Exigir falhas e recuperação controladas de Redis/Worker, com estado visível, retomada segura e sem efeito duplicado.
- Preservar a análise do Reactive Resume como atividade opcional posterior. AC-M0-003 deixa de ser gate de M0 por decisão explícita; o relatório existente não foi descartado nem validado novamente.
- Entrevista guiada em andamento, com até duas decisões por rodada. Implementação de M0 ainda não iniciada.
- Web deve abrir já autorizada pela sessão local Linux, sujeito a validação do mecanismo; a API permanece autenticada. Checks apenas locais em M0; CI fica para marco posterior.
- CI será introduzido em M1. Hermes e Codex são os alvos escolhidos para M0.5, que mantém execução e gate separados.
- Interface de M0: uma execução ativa por vez, sem histórico navegável, último estado/resultado restaurado ao reabrir. Proposta inicial de campos/estados aprovada e registrada no contexto; tipos e limites ainda serão especificados.
- A Web abre autorizada por comando local; URL direta sem sessão válida permanece bloqueada. Dados sintéticos isolados por ambiente, testes temporários, logs JSON no terminal sem arquivo por padrão e limpeza manual explícita.
- Sessão válida até reinício da API. Diagnóstico limitado a 120 s no total, até três tentativas de até 30 s; falha terminal permite nova intenção, sem duplicação em reentrega.

## Fonte e reconciliação

Foram importados 59 arquivos públicos de especificação e referência: documentos raiz, `docs/` e `assets/`. Os hashes da fonte estão em [package-import-2026-11-11.json](package-import-2026-11-11.json). `PROJECT_SOURCE.md` permanece idêntico ao pacote aprovado. O pacote de origem não foi alterado.

Não foram importados `private/`, `old/` nem o `PACKAGE_MANIFEST.json` original, que inventaria também arquivos privados. O `.gitignore` do repositório preserva as exclusões anteriores e incorpora Python e os nomes de artefatos privados do pacote.

As notas do Obsidian usadas como contexto foram `Resume Builder`, `Planning Summary`, `Specification Refresh 2026-11-11`, `Vertical Slices and Milestone Roadmap` e `Vertical Slices/M0`, em `10 Projects/Personal/Resume Builder/`. A nota de refresh prevalece sobre a stack descrita nas notas de 04/11. Nenhum conteúdo privado dessas fontes foi incorporado. O vault não foi modificado nesta sincronização.

## Adaptações locais

- Stack ativa: React/Vite, FastAPI/Python, SQLAlchemy 2/Alembic, Dramatiq/Redis, pnpm + uv + justfile, Pytest/Vitest e structlog.
- ADRs antigos e endereços de módulos/contratos renomeados apontam aos documentos atuais, preservando links existentes. A versão anterior permanece no histórico Git, commit `d2ba2e0abd88190af5d9ec41989c8f6d4342f6c2`.
- Documentos complementares de engenharia, requisitos, dependências e riscos foram reconciliados com a stack nova. Os IDs REQ existentes foram preservados; M1 inclui a importação privada pendente de revisão e M2 os templates visual/ATS aprovados.
- `AGENTS.md` explicita a distinção já aprovada entre Playwright Python para exportação de PDF local e a proibição de automação de candidaturas pelo backend.
- O README descreve a exclusão efetiva dos materiais privados. Gerador de referência e exemplos de contrato/configuração continuam referências; não foram executados ou promovidos a runtime de produção.
- A inicialização de 04/11 e seu manifesto foram preservados em `docs/history/`. O manifesto na raiz passa a descrever o conjunto público atual, não o pacote original.

## Limites de execução

Esta mudança atualiza documentação e referências. Não instala dependências, não gera lockfiles, não inicia Web/API/Worker/Redis, não executa providers ou clientes MCP, não faz commit/push e não declara M0 concluído. A construção e exportação do currículo continuam em M1/M2/M3; M0.5 permanece um spike separado.

As decisões funcionais estão em [context.md](../.specs/features/m0-foundation/context.md), e a proposta de critérios verificáveis está em [spec.md](../.specs/features/m0-foundation/spec.md), ainda para revisão. Critérios herdados: [AC-M0-001/002](roadmap/acceptance-criteria.md).

## Verificações executadas

- `git diff --check`: PASS.
- `sha256sum --check --quiet MANIFEST.sha256`: PASS para o conjunto público atual.
- Verificação local dos links Markdown relativos: PASS; links externos e âncoras não foram validados.
- Hashes da fonte pública comparados com o registro de importação: fonte inalterada. Adaptações de README, AGENTS e índice documental estão descritas acima.
- Parsing de sintaxe Python via `ast.parse` dos dois exemplos/geradores importados: PASS; sem importar dependências ou executar os scripts.
- `validate_spec.py .specs/features/m0-foundation/spec.md --strict`: PASS estrutural, sem erros ou warnings; não valida implementação nem substitui revisão das propostas.
- Busca limitada por padrões de chave privada, tokens GitHub/OpenAI e valores de e-mail: nenhum resultado no conteúdo público examinado. Não equivale a auditoria completa.
- Materiais `private/` ausentes deste checkout; pacotes e serviços de aplicação não foram instalados/iniciados/testados.
