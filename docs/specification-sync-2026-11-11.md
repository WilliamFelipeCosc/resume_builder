# Sincronização da especificação — 2026-11-11

> Registro histórico da importação inicial. As seções até “Verificações executadas” descrevem o estado anterior à implementação. A sincronização posterior à conclusão do M0 está registrada no final deste documento; o pacote original permanece preservado.

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

## Sincronização posterior — M0 concluído e aceito

Atualização do Obsidian solicitada pelo proprietário em 2026-11-11, após confirmar às 16:53 (America/Sao_Paulo) abertura autorizada no navegador e diagnóstico concluído com sucesso. O estado publicado no vault deriva do repositório até `a151610`: implementação `f35b4e0`, validação independente `a9c25a9` e aceite manual `a151610`. Esses commits são locais; esta sincronização não fez push.

Seis notas existentes foram atualizadas em `10 Projects/Personal/Resume Builder/`:

- `Resume Builder.md`: painel ativo, M0 concluído, próximo passo M0.5, critérios e log.
- `Planning Summary.md`: stack atual, roadmap, evidências e decisões OPEN atuais.
- `Specification Refresh 2026-11-11.md`: distinção entre pacote histórico preservado e execução atual; M0 concluído.
- `Vertical Slices and Milestone Roadmap.md`: M0/VS-M0-01/02 concluídos, evidências, checklist e clientes-alvo do spike.
- `Vertical Slices/M0.md`: status `done`, planejamento `APPROVED`, execução `DONE`, contratos, testes, aceite e comandos de operação.
- `Vertical Slices/Vertical Slices.md`: índice ativo e progresso por marco.

Evidências reproduzidas: T1–T22 concluídas; 23/23 FNDs e AC-M0-001/002 verificados; 254 Pytest, 17 Vitest e 3 Chromium aprovados; oito mutações detectadas pelo Verifier. São resultados da execução já registrada em [validation.md](../.specs/features/m0-foundation/validation.md), e não novos testes rodados durante esta atualização documental. O relato manual do proprietário permanece separado da evidência automatizada.

M0.5 mantém gate/autorização próprios e execução NOT_RUN, com Hermes e Codex como alvos. M1–M7 permanecem não executados; prioridade M3, CI em M1 e ADRs aprovados preservados. O texto legado dos marcos futuros continua subordinado às especificações atuais; não foi convertido em aprovação de implementação. Nenhum material privado foi copiado ao vault nem ao Git.

Verificação desta sincronização: seis notas relidas pelo conector Obsidian, sem links internos não resolvidos e sem afirmações globais obsoletas de M0 NOT_RUN. Status, contagens e commits comparados às evidências do repositório. `git diff --check` e manifesto SHA-256 verificados após a atualização. Não houve mudança de runtime ou de requisitos aprovados.
