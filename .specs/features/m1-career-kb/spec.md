# M1 — Career KB Core Specification

**Status:** APPROVED; Design aprovado em 2026-11-16; Tasks e ferramentas aprovadas em 2026-11-16 às 20:09 (-03); execução autorizada em 2026-11-16 às 20:17 (-03); baseline concluída; implementação em andamento.
**Date:** 2026-11-16.
**Context:** [context.md](context.md).

## Problem Statement

A aplicação dispõe do diagnóstico M0 e do spike MCP sintético, mas ainda
não mantém fatos profissionais reais. M2/M3 precisam consultar fatos com
identidade, versões, fontes e permissões, sem promover dados importados
a qualificações confirmadas automaticamente.

O plano Obsidian tem três slices de CRUD/relações/revisão, mas o aceite M1
também exige importação privada, staging, decisões em lote e reversão.
Esta especificação cobre o marco completo sem antecipar importadores M6.

## Goals

- [ ] Demonstrar cadastro, consulta, edição, arquivamento, relações e revisões
  de todas as entidades core com dados fictícios.
- [ ] Demonstrar staging, dedup, revisão individual/lote, auditoria e undo
  antes de executar a carga privada.
- [ ] Reutilizar fatos autorizados com IDs e fontes nos próximos marcos.
- [ ] Introduzir GitHub Actions antes da implementação do domínio.
- [ ] Concluir AC-M1-001/002/003 com evidências separadas de testes sintéticos
  e revisão local dos dados privados.

## Out of Scope

| Feature | Reason |
| --- | --- |
| Extração PDF automática e importadores gerais | M1 usa o seed preparado; ingestão completa permanece em M6 |
| ResumeDocument, preview e exportação de currículo | M2; `resume_document_seed.json` não é carga da KB |
| Tailoring, embeddings e provider de IA | M3/M6; não necessários para validar a verdade profissional |
| MCP com fatos reais e auth HTTP MCP | M4; manter o spike M0.5 isolado |
| Exclusão definitiva de fatos e histórico pela UI M1 | Proprietário escolheu arquivamento |
| Push, ativação remota de CI e publicação sem autorização | Revisão deste plano não autoriza ações remotas |
| Alterações em requisitos aprovados ou ADRs DECIDED | Exigem aprovação específica |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Sequência da carga | Piloto fictício completo e validado antes da carga privada | Exercitar riscos sem usar dados pessoais como fixtures | Sim, entrevista |
| Remoção | Arquivar, preservar vínculos/histórico | Evitar destruir proveniência e futuras referências | Sim, entrevista |
| Aceite e veracidade | Aceitar pode manter unverified; confirmar é ação explícita | Importação aceita não prova qualificação | Sim, entrevista |
| Edição de conteúdo confirmado | Nova revisão com unidade alterada unverified; revisão anterior preservada | Confirmação anterior não se transfere a conteúdo diferente; campos independentes do Profile preservados | Sim, entrevista |
| Lote | Tudo ou nada, com itens bloqueantes identificados | Evitar resultado parcial inesperado | Sim, entrevista |
| Undo após edição posterior | Bloquear os itens alterados e pedir revisão | Não sobrescrever trabalho posterior | Sim, entrevista |
| Correspondência ambígua | Sugerir e aguardar create/update/link/ignore | Sem merge automático por nome/período | Sim, entrevista |
| Repetição do mesmo PDF com seed modificado | Reutilizar identidade da fonte e apresentar diferenças para revisão | Hash da fonte sozinho não identifica uma proposta de importação | Sim, consolidação |
| Dependências bloqueantes no undo | Tratar mudanças posteriores em vínculos como bloqueantes; seleção de undo é atômica | Preservar integridade e consistência com lote tudo ou nada | Sim, consolidação |
| Matriz de campos e permissões, limites, contratos e schema SQL | Apresentar no design para aprovação antes de código | O seed é preparatório e os contratos atuais são conceituais; não presumir campos/cardinalidades | Gate de design |
| Estilização | Tailwind CSS com tokens padrão | Escolha explícita; sem paleta própria M1 | Sim, entrevista técnica |
| Consultas frontend | TanStack Query sobre cliente OpenAPI gerado | Escolha explícita; convenções de cache/mutações no design | Sim, entrevista técnica |
| Componentes | shadcn/ui, somente componentes necessários, com cores padrão do Tailwind | Escolha explícita na entrevista técnica para as necessidades M1 | Sim, entrevista técnica |
| Formulários | React Hook Form; erros da API por campo; Pydantic/OpenAPI como autoridade | Escolha explícita; sem nova biblioteca de schemas neste momento | Sim, entrevista técnica |
| Navegação e renderização | React Router Data Mode como SPA no Vite; API FastAPI; dados da API no TanStack Query | Escolha explícita; URLs diretas, erros por rota e proteção de alterações pendentes | Sim, entrevista técnica |
| Estado frontend | Query para API, React Hook Form para rascunhos, URL para filtros compartilháveis e estado local para seleção/diálogos | Escolha explícita; sem store global inicialmente | Sim, entrevista técnica |
| Organização frontend | Feature-based; páginas/componentes/hooks/API por funcionalidade e elementos genéricos compartilhados | Adendo explícito do proprietário | Sim, entrevista técnica |
| Organização backend | Módulos por funcionalidade com responsabilidades internas separadas; serviços autorizados reutilizáveis | Escolha explícita na entrevista técnica | Sim, entrevista técnica |
| Histórico | Estado atual, revisões imutáveis e auditoria; undo por nova revisão | Escolha explícita; preservar histórico e bloquear sobrescrita posterior | Sim, entrevista técnica |
| Persistência KB | SQLAlchemy ORM declarativo interno aos repositórios; DTOs Pydantic na API | Escolha explícita; representar relações do novo domínio | Sim, entrevista técnica |
| Unidade de confirmação | Campo no Profile; entidade nos demais registros; proveniência por campo quando fornecida e privacidade por campo mais restritiva | Escolha explícita; confirmação não se estende a dados independentes ou alterados | Sim, entrevista técnica |
| Conflitos de edição | Rejeitar revisão-base obsoleta, preservar rascunho e comparar manualmente | Escolha explícita; sem merge automático | Sim, entrevista técnica |
| Preparação da importação | Execução direta e limitada no M1; limites no design | Escolha explícita; seed pequeno, sem IA/extração automática ou novo job de worker | Sim, entrevista técnica |
| Armazenamento das fontes | Cópias imutáveis privadas XDG, verificadas por hash, preservando originais externos | Escolha explícita; manter fontes disponíveis independentemente da pasta externa | Sim, entrevista técnica |
| Privacidade inicial | Documento, staging e fatos aceitos confidential; mudanças explícitas na revisão; liberar fato não libera PDF | Escolha explícita; importação privada por padrão | Sim, entrevista técnica |
| Paginação | Offset/limite, filtros e ordenação estável no backend | Escolha explícita; limites numéricos e desempate no design | Sim, entrevista técnica |
| Revisão-base no transporte | Corpo tipado; conflito HTTP 409; comparação e escrita atômicas, incluindo revisões dos itens do lote | Escolha explícita após comparação das alternativas | Sim, entrevista técnica |
| Abordagem do modelo KB | Tabelas tipadas por entidade para estado atual, histórico imutável e metadados por campo | Escolha explícita após comparação com registros genéricos JSON | Sim, início do Design |
| Fonte manual de T16 | text obrigatório até 8.000, title opcional até 256 e idempotencyKey UUID; texto UTF-8 imutável por hash e confidential inicial | Fechar lacuna do DTO sem presumir campos; anotação não confirma qualificações | Sim, proprietário em 2026-11-17 às 08:56 (-03) |

**Open questions: none** — contexto e propostas complementares foram
aprovados para Design. Campos,
cardinalidades e limites são entregáveis do design, não schemas implícitos
aprovados por este texto. Sua aprovação é obrigatória antes da implementação.

## User Stories

Todas as histórias abaixo são P1 do M1; a ordem representa dependências,
não dispensa qualquer história do aceite completo.

### P1: S1 — Preparar execução reproduzível

**User Story:** Como proprietário, quero checks reproduzíveis antes do
domínio para detectar regressões sem depender de dados privados.

**Acceptance Criteria**:
1. WHEN a execução M1 começar THEN o projeto SHALL preparar o workflow GitHub Actions antes de implementar o domínio KB, cobrindo Python, web, contratos, browser e lint existentes com fixtures sintéticas. (MONE-01)
2. IF o workflow não tiver sido executado no runner remoto THEN o relatório SHALL registrar CI remoto como não validado, distinguindo resultados locais e sem alegar execução por inspeção do YAML. (MONE-02)

**Independent Test:** Conferir configuração e executar os checks locais;
registrar execução remota somente após push autorizado. Falha intermitente
de worker deve ser investigada e registrada, sem ocultá-la com retries.

### P1: S2 — Cadastrar e relacionar fatos autorizados

**User Story:** Como proprietário, quero manter uma KB consultável com
fontes, relações e privacidade para reutilizar informações revisadas.

**Acceptance Criteria**:
1. WHEN o usuário autorizado cadastrar, consultar ou editar Profile, Experience, Statement, Project, Achievement, Skill, Education, Language ou Evidence THEN a KB SHALL preservar os valores fornecidos conforme o contrato aprovado, identidade, revisão, proveniência, confirmação e classificação aplicáveis. (MONE-03)
2. WHEN o usuário vincular entidades existentes THEN a KB SHALL preservar as identidades das entidades e a proveniência do vínculo. (MONE-04)
3. IF um vínculo apontar para entidade inexistente THEN a KB SHALL rejeitar a operação sem persistir vínculo pendente ou alteração parcial. (MONE-05)
4. IF o principal não tiver autorização para a operação THEN o serviço SHALL rejeitá-la antes de recuperar conteúdo privado ou modificar estado. (MONE-06)
5. WHEN uma consulta autorizada tiver escopo inferior à privacidade de um campo ou fonte THEN a resposta SHALL omitir esse conteúdo também nas relações, revisões e diffs retornados. (MONE-07)
6. WHEN o usuário arquivar um fato THEN a KB SHALL preservar seus vínculos e revisões para consulta histórica autorizada. (MONE-08)

**Independent Test:** Perfil fictício completo com todas as entidades;
round trip por UI/API, referências inválidas, escopos distintos e arquivo
de registro já vinculado. AC-M1-001 inclui Achievement/Evidence por
REQ-KB-001, mesmo com enumeração abreviada na tabela do AC.

### P1: S3 — Corrigir e confirmar sem sobrescrita silenciosa

**User Story:** Como proprietário, quero comparar e revisar fatos para
distinguir conteúdo atual, histórico e confirmação explícita.

**Acceptance Criteria**:
1. WHEN o usuário editar conteúdo confirmed THEN a KB SHALL criar uma nova revisão com a unidade alterada unverified, preservando a revisão anterior e a confirmação dos campos independentes não alterados do Profile. (MONE-09)
2. WHEN o usuário confirmar explicitamente uma unidade unverified THEN a KB SHALL registrar confirmação vinculada àquela unidade, revisão e responsável autorizado, usando campo no Profile e entidade nos demais registros. (MONE-10)
3. WHEN o usuário rejeitar uma proposta de alteração THEN a KB SHALL preservar a revisão canônica anterior. (MONE-11)
4. IF a revisão-base de uma escrita estiver obsoleta THEN a KB SHALL rejeitar a escrita com conflito HTTP 409, preservando a revisão atual e o rascunho da UI para comparação manual, sem merge automático. (MONE-12)
5. WHEN o usuário consultar o histórico autorizado THEN a KB SHALL apresentar valores anteriores, fontes e diferenças entre revisões sem apagar proveniência. (MONE-13)

**Independent Test:** Editar fato confirmado em duas sessões, confirmar
a nova revisão explicitamente, rejeitar outra proposta e inspecionar
o histórico. A escrita da sessão obsoleta não altera o resultado atual.
As operações recebem revisão-base no corpo tipado; a comparação e a escrita
são atômicas no banco, inclusive para as revisões afetadas por um lote.

### P1: S4 — Importar para staging privado

**User Story:** Como proprietário, quero revisar propostas do seed
antes que elas alterem a KB ou sejam tratadas como qualificações.

**Acceptance Criteria**:
1. WHEN o usuário selecionar o documento-fonte e o seed suportado THEN a importação SHALL validar associação por hash e referências de fonte/página antes de criar candidatos revisáveis. (MONE-14)
2. IF houver schema não suportado, referência inválida ou divergência de hash THEN a importação SHALL rejeitar a entrada sem criar fatos canônicos. (MONE-15)
3. WHEN uma importação válida terminar THEN a KB SHALL apresentar candidatos em staging pending_review com classificação confidential sem confirmar ou criar fatos canônicos automaticamente. (MONE-16)
4. The adapter SHALL preservar texto original, proveniência por campo quando fornecida, valores desconhecidos, temporalidade histórica, menções a skills e rótulos editoriais sem convertê-los em afirmações novas. (MONE-17)
5. WHEN o mesmo documento e proposta forem importados novamente THEN a KB SHALL reutilizar a importação existente sem duplicar candidatos ou fatos. (MONE-18)
6. WHEN a mesma fonte receber uma proposta diferente THEN a KB SHALL apresentar diferenças para revisão sem sobrescrever fatos existentes. (MONE-19)
7. WHEN houver correspondência ambígua por nome ou período THEN o staging SHALL mostrar a sugestão e aguardar decisão humana create/update/link/ignore. (MONE-20)

**Independent Test:** Fixture sintética com a estrutura observada do seed;
reimportação, proposta alterada, hash divergente, links inválidos e
ambiguidades históricas. Contagens do seed privado não são thresholds
universais nem fatos confirmados.

### P1: S5 — Aplicar decisões auditáveis

**User Story:** Como proprietário, quero revisar individualmente ou em
lote e saber exatamente quais alterações foram aplicadas.

**Acceptance Criteria**:
1. WHEN o usuário revisar um candidato THEN o staging SHALL mostrar fonte, classificação, diferenças e ação proposta create/update/link/ignore antes do commit. (MONE-21)
2. WHEN o usuário aceitar uma importação sem confirmar a declaração THEN a KB SHALL manter o conteúdo aceito unverified. (MONE-22)
3. IF qualquer decisão selecionada estiver inválida ou em conflito THEN o commit do lote SHALL rejeitar todas as decisões selecionadas e identificar os itens bloqueantes sem escrita canônica parcial. (MONE-23)
4. WHEN um lote válido for aplicado THEN a KB SHALL persistir decisões, alterações e auditoria na mesma transação lógica. (MONE-24)
5. WHEN uma decisão já aplicada for repetida com a mesma chave e conteúdo THEN o serviço SHALL retornar o resultado original sem repetir alterações. (MONE-25)
6. IF a mesma chave idempotente for reutilizada com conteúdo diferente THEN o serviço SHALL retornar conflito sem novas alterações. (MONE-26)
7. WHEN o usuário aprovar, rejeitar, confirmar, arquivar ou reverter uma alteração THEN a auditoria SHALL registrar responsável, fonte, ação, instante e revisões afetadas. (MONE-27)

**Independent Test:** Decisão individual, lote misto válido/inválido,
replay idempotente, chave divergente e reconstrução auditável das ações.
Aceite da importação e confirmação são ações distintas na interface.

### P1: S6 — Reverter com segurança e preservar a fonte

**User Story:** Como proprietário, quero desfazer alterações importadas
sem perder o documento original ou sobrescrever edições posteriores.

**Acceptance Criteria**:
1. WHEN o usuário reverter alterações sem mudanças posteriores ou dependências bloqueantes THEN a KB SHALL restaurar o estado lógico anterior por novas revisões auditáveis. (MONE-28)
2. IF um item selecionado para undo tiver mudança posterior no conteúdo ou em vínculos dependentes THEN a KB SHALL bloquear a seleção e identificar os itens que exigem revisão sem sobrescrever o estado atual. (MONE-29)
3. The sistema SHALL preservar os bytes dos originais externos e das cópias imutáveis privadas XDG do PDF e do seed durante importação, revisão e reversão, verificando a integridade das cópias por hash. (MONE-30)
4. IF houver falha antes de concluir uma operação de escrita THEN a KB SHALL impedir a exposição de fatos canônicos parcialmente aplicados. (MONE-31)
5. WHEN a aplicação reiniciar após commit THEN a KB SHALL recuperar fatos, decisões, recibos idempotentes e histórico já persistidos. (MONE-32)

**Independent Test:** Criar, atualizar e vincular via importação; reverter
um caso sem conflito; bloquear undo após edição posterior e após novo
vínculo; reiniciar e conferir persistência. Comparar hash do PDF antes/depois.

### P1: S7 — Fechar piloto e carga privada com evidências

**User Story:** Como proprietário, quero validar o fluxo fictício antes
de revisar dados pessoais e liberar a base para M2/M3.

**Acceptance Criteria**:
1. The suíte automatizada e seus artefatos SHALL usar exclusivamente dados fictícios, sem valores pessoais dos arquivos privados. (MONE-33)
2. The logs operacionais SHALL excluir conteúdo de currículo, trechos, contatos, cookies, credenciais e payloads privados de erro. (MONE-34)
3. WHEN os fluxos sintéticos estiverem implementados THEN o projeto SHALL executar os gates e uma verificação independente com testes derivados dos critérios e sensor de discriminação antes da carga privada. (MONE-35)
4. WHEN o piloto fictício tiver sido validado THEN a aplicação SHALL permitir revisão humana local do seed privado sem autoaprovação dos candidatos. (MONE-36)
5. WHEN o M1 for apresentado para aceite THEN o relatório SHALL distinguir testes sintéticos, revisão privada, itens ainda pendentes e resultados de CI local/remoto. (MONE-37)
6. The registro de execução SHALL separar intervalos ativos, espera, retrabalho e limitações de medição conforme o modelo de esforço do projeto. (MONE-38)

**Independent Test:** Fluxo UI/API fictício completo, testes negativos de
autorização, inspeção de logs/artefatos com sentinelas sintéticas, relatório
independente, demonstração local privada e revisão do registro de esforço.

## Edge Cases

- IF a revisão de staging estiver pendente THEN consultas de fatos canônicos SHALL excluir seus candidatos.
- IF uma evidência estiver ausente THEN a UI SHALL mostrar a ausência sem inventar comprovação.
- IF uma data ou atualidade não tiver sido informada THEN a KB SHALL preservar o desconhecimento em vez de preencher a partir da data atual.
- IF a fonte usar apenas referência documental THEN a KB SHALL preservar essa origem sem apresentá-la como evidência independente de veracidade.

## Requirement Traceability

| Requirement ID | Story / cobertura | Phase | Status |
| --- | --- | --- | --- |
| MONE-01 | S1: CI antes do domínio; roadmap M1 | T2 e tarefas restantes | In Progress (CI remoto NOT_RUN) |
| MONE-02 | S1: evidência remota distinta; REQ-QA-001 | T2 e tarefas restantes | In Progress (CI remoto NOT_RUN) |
| MONE-03 | S2: core completo; REQ-KB-001/002, AC-M1-001 | T3, T16 e tarefas restantes | In Progress (fonte manual privada) |
| MONE-04 | S2: vínculos; REQ-KB-001/002, AC-M1-001 | T12 e tarefas restantes | In Progress (fundação de histórico) |
| MONE-05 | S2: integridade referencial; AC-M1-001 | T12 e tarefas restantes | In Progress (fundação de histórico) |
| MONE-06 | S2: autorização pré-leitura/escrita; REQ-SEC-001 | T13, T16, T17 e tarefas restantes | In Progress (projeção e fontes autorizadas) |
| MONE-07 | S2: privacidade por campo/fonte; REQ-KB-002, REQ-SEC-001 | T13, T17 e tarefas restantes | In Progress (projeção e fontes autorizadas) |
| MONE-08 | S2: arquivo histórico; AC-M1-001 | T12 e tarefas restantes | In Progress (fundação de histórico) |
| MONE-09 | S3: edição sem confirmação herdada; AC-M1-001 | Tasks | In Tasks |
| MONE-10 | S3: confirmação explícita; REQ-KB-002 | Tasks | In Tasks |
| MONE-11 | S3: rejeição sem overwrite; AC-M1-001 | Tasks | In Tasks |
| MONE-12 | S3: concorrência; REQ-KB-002 | T11 e tarefas restantes | In Progress (transação explícita) |
| MONE-13 | S3: histórico/diff; AC-M1-001 | T13 e tarefas restantes | In Progress (projeção autorizada) |
| MONE-14 | S4: associação fonte/seed; AC-M1-002 | T8, T14, T15 e tarefas restantes | In Progress (entrada e PDF limitado) |
| MONE-15 | S4: validação negativa; AC-M1-002 | T8, T15 e tarefas restantes | In Progress (entrada e PDF limitado) |
| MONE-16 | S4: staging privado; REQ-KB-004, AC-M1-002 | Tasks | In Tasks |
| MONE-17 | S4: semântica histórica; REQ-KB-002/004, AC-M1-002 | Tasks | In Tasks |
| MONE-18 | S4: dedup da proposta; AC-M1-002 | Tasks | In Tasks |
| MONE-19 | S4: diferenças da proposta; AC-M1-002 | Tasks | In Tasks |
| MONE-20 | S4: dedup ambígua; REQ-KB-004 | Tasks | In Tasks |
| MONE-21 | S5: decisões/diff; AC-M1-003 | Tasks | In Tasks |
| MONE-22 | S5: aceite sem confirmar; AC-M1-002/003 | T16 e tarefas restantes | In Progress (anotação não cria fatos) |
| MONE-23 | S5: lote atômico; AC-M1-003 | T11 e tarefas restantes | In Progress (transação explícita) |
| MONE-24 | S5: commit e auditoria; AC-M1-003 | T11 e tarefas restantes | In Progress (transação explícita) |
| MONE-25 | S5: replay idempotente; REQ-KB-004 | Tasks | In Tasks |
| MONE-26 | S5: conflito idempotente; REQ-KB-004 | T7 e tarefas restantes | In Progress (contrato de erros) |
| MONE-27 | S5: auditoria; AC-M1-003 | T12, T16 e tarefas restantes | In Progress (auditoria de fonte manual) |
| MONE-28 | S6: reversão auditável; AC-M1-003 | Tasks | In Tasks |
| MONE-29 | S6: bloqueio de undo; AC-M1-003 | T7 e tarefas restantes | In Progress (contrato de erros) |
| MONE-30 | S6: PDF imutável; AC-M1-003 | T12, T14, T16, T17 e tarefas restantes | In Progress (fonte por hash e download verificado) |
| MONE-31 | S6: falha sem parcial; AC-M1-001/003 | T11, T14 e tarefas restantes | In Progress (transação explícita e instalação atômica) |
| MONE-32 | S6: durabilidade; REQ-KB-002/004 | T12, T14 e tarefas restantes | In Progress (histórico e arquivo durável) |
| MONE-33 | S7: fixtures privadas proibidas; REQ-SEC-001 | T2 e tarefas restantes | In Progress (CI remoto NOT_RUN) |
| MONE-34 | S7: logs sem conteúdo privado; REQ-SEC-001 | T13, T15, T17 e tarefas restantes | In Progress (parser e fonte protegidos) |
| MONE-35 | S7: verificação do piloto; REQ-QA-001 | T4 e tarefas restantes | In Progress (descoberta preparada) |
| MONE-36 | S7: carga privada revisada; AC-M1-002/003 | Tasks | In Tasks |
| MONE-37 | S7: evidência e limitações; AC-M1-001/002/003 | Tasks | In Tasks |
| MONE-38 | S7: piloto medido; workflow de estado/esforço | T1, T61–T64 | In Progress (T1 baseline registrado) |

**Coverage:** 38 requisitos mapeados às 64 tarefas propostas; a matriz requisito→tarefa está em [tasks.md](tasks.md). Nenhuma tarefa foi executada ou marcada Verified.
MONE-01/02 correspondem aos dois critérios de S1, respectivamente.
Edge Cases especializam MONE-16/17/21 sem novos requisitos independentes.

## Dimension Sweep

| Dimension | Cobertura / gate |
| --- | --- |
| Input validation & bounds | MONE-14/15; design deve fixar limites numéricos e contratos antes de código |
| Failure / partial failure | MONE-23/24/31; design da coordenação DB/arquivos |
| Idempotency / retry / duplicates | MONE-18/19/20/25/26 |
| Auth boundaries & rate limits | MONE-06/07/34; matriz e limites de requests no design, sem alterar HTTP MCP M4 |
| Concurrency / ordering | MONE-12/23/29 |
| Data lifecycle | MONE-08/28/29/30; sem purge/TTL M1, pois histórico e fonte são preservados |
| Observability | MONE-27/34/37/38; auditoria distinta de log operacional |
| External-dependency failure | MONE-02/31; sem provider remoto; CI e arquivos locais com falhas explícitas |
| State-transition integrity | MONE-09/10/11/16/22/23/28/29 |

## Execution Outline

Este é o sequenciamento proposto, não um `tasks.md` aprovado:

1. Aprovar contexto/spec e projetar contratos, relações, permissões e limites.
2. Preparar CI e registrar baseline local; execução remota depende de push autorizado.
3. Entregar Profile + Experience/Project com fonte e revisão na UI.
4. Completar entidades, relações e arquivamento de VS-M1-02.
5. Entregar revisão/confirmação/histórico de VS-M1-03.
6. Entregar staging, dedup e decisões/undo sintéticos com gates próprios,
   cobrindo explicitamente a lacuna do detalhamento Obsidian.
7. Verificar o piloto completo antes da carga privada.
8. Exercitar importação privada, revisão humana e limitações sem publicar dados.
9. Verificar o conjunto final, apresentar aceite e registrar retrospectiva do esforço.

Antes de Tasks: analisar limite global atual de 1 KiB, capacidades locais
restritas ao diagnóstico, ativação de foreign keys nas conexões SQLite,
migrações existentes, schema preparatório do seed e harness Docker/Chromium.
São pontos observados na análise, não correções já realizadas.

## Success Criteria

- [ ] AC-M1-001/002/003 demonstrados, incluindo Achievement e Evidence.
- [ ] Gates `just check` e checks específicos M1 executados com resultados reais.
- [ ] CI no runner verificado após autorização remota; se indisponível,
  pendência explicitada, sem alegar validação remota.
- [ ] Piloto fictício aprovado antes da carga privada.
- [ ] Carga privada revisável, com fonte preservada e pendências explícitas;
  dados pendentes não precisam ser falsamente confirmados para encerrar o marco.
- [ ] Verificação independente final com evidências e sensor; aceite humano
  registrado antes de promover estado canônico para accepted.
- [ ] Obsidian reconciliado por revisão manual autorizada, mantendo o repo
  como fonte de estado; sem alegação de sincronia baseada em snapshot antigo.
