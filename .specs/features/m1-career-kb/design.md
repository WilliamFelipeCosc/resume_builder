# M1 — Career KB Core Design

**Spec:** [spec.md](spec.md). **Context:** [context.md](context.md).
**Status:** Approved pelo proprietário em 2026-11-16, às 17:32 (-03),
para detalhamento de Tasks. Tarefas aprovadas em 2026-11-16 às 20:09 (-03);
implementação aguarda comando explícito de início, conforme pedido do proprietário.
**Date:** 2026-11-16. **Base examinada:** `d2a609d`.

## Architecture Overview

Manter monólito modular local, com frontend Feature-based e backend por
funcionalidade. Routers HTTP adaptam DTOs para serviços autorizados;
serviços controlam transações e chamam repositórios ORM e armazenamento
privado. API e futuro MCP compartilham serviços; MCP real fica em M4.
M0.5 permanece em seu banco isolado.

A entrevista aprovou ORM, estado atual + revisões imutáveis e auditoria,
SPA/Data Mode, formulários e consultas separados, fontes privadas XDG e
preparação direta do seed. O início do Design comparou as abordagens abaixo;
o proprietário aprovou a primeira antes do detalhamento.

| Abordagem | Benefício | Custo | Decisão |
| --- | --- | --- | --- |
| Tabelas tipadas por entidade, histórico imutável e metadados por campo | Integridade relacional e consultas explícitas | Mais tabelas e migrations | Aprovada |
| Registros genéricos JSON com validação por tipo | Menos tabelas e evolução flexível de payload | Mais validação e cuidado com índices, vínculos e projeções privadas | Não escolhida |

**Limite desta aprovação:** nomes, campos, cardinalidades e budgets abaixo
foram aprovados na revisão do design; os títulos "proposed" preservam a
forma em que foram apresentados. Não são schemas executáveis existentes.
Compatibilidade e limites precisam passar pelos gates definidos. Não alterar
PROJECT_SOURCE ou ADRs DECIDED para acomodar estas propostas silenciosamente.

## Code Reuse Analysis

| Componente existente | Reuso / ajuste proposto |
| --- | --- |
| `resume_api.app.Boundary` | Preservar sessão/Host/Origin antes de leitura; selecionar política de payload por rota conhecida |
| `resume_api.session` e `launcher` | Bootstrap local de uso único e cookie same-origin; sem nova autenticação M1 |
| `resume_core.service.Principal` | Manter identidade/capabilities imutáveis e checagem prévia; acrescentar escopos KB concedidos na composição confiável |
| `resume_core.database.make_engine` | Mesma infraestrutura SQLite/WAL; habilitar foreign keys em toda conexão |
| `backend/migrations` | Acrescentar revisões após `0001_diagnostics`; sem create_all no startup |
| `resume_core.paths.EnvironmentPaths` | Dados/fontes em XDG privado; testes em raiz temporária dedicada |
| `packages/api-client` | Mesmo gerador OpenAPI/SDK fetch; tipos TS não são reescritos à mão |
| `tools.check_contract` | Export offline e duas gerações determinísticas do SDK |
| `logging_policy` | Estender allowlists com nomes estáticos, sem payloads, paths arbitrários ou trechos |
| `justfile` e harness web | Gates atuais, processo real e isolamento sintético; incluir os novos testes nas seleções |

Usar o banco atual `paths.data / "diagnostics.sqlite3"` para as tabelas KB
também. O nome é legado; renomear banco não integra M1. Isso permite uma
única transação para fatos, vínculos, revisões, auditoria e recibos M1.

## Components

### Frontend

Organização proposta sob `apps/web/src/`:

| Área | Responsabilidade e dependências |
| --- | --- |
| `app/` | Composição dos providers, router, sessão e layout; importa entradas públicas das features |
| `features/diagnostics/` | Encapsular a tela existente sem misturar diagnóstico com KB |
| `features/career-kb/` | Lista/detalhe/cadastro das entidades, relações, hooks Query e adaptadores dos formulários |
| `features/fact-review/` | Histórico/diff, confirmação por unidade e tratamento de conflito |
| `features/imports/` | Seleção dos dois arquivos, staging, correspondências, decisões e undo |
| `shared/ui/` | Componentes genéricos shadcn/ui efetivamente usados |
| `shared/api/` | Configuração do cliente gerado, normalização de erros e cancelamento |
| `shared/lib/` | Utilitários genéricos sem dependência de features |

Features expõem entradas públicas; proibir imports profundos entre features.
`shared` não importa features. Tipos de transporte vêm do pacote gerado;
modelos de formulário locais representam somente rascunhos/transformações
de UI, não uma cópia dos DTOs.

React Router Data Mode com `createBrowserRouter`/`RouterProvider`, sem plugin
Framework Mode. Rotas propostas: `/diagnostics`, `/career`, `/career/profile`,
`/career/:kind`, `/career/:kind/:id`, `/career/:kind/:id/edit`,
`/career/:kind/:id/history`, `/imports`, `/imports/:batchId`.
`:kind` é whitelist fechada, não acesso dinâmico a tabelas. A raiz redireciona
para a KB após bootstrap. URLs não contêm nomes, contatos ou trechos.

O backend entrega index.html somente para rotas UI reconhecidas. `/api/*`,
arquivos inexistentes e paths arbitrários nunca recebem fallback HTML.
O shell estático não contém dados privados e pode ser entregue antes da
sessão; chamadas privadas continuam autenticadas. Preservar limpeza do
fragmento de bootstrap antes de iniciar router e consultas.

### Convenções de UI, dados e formulários

- Tailwind com tokens padrão; proposta de cores neutras da escala padrão.
  shadcn com utilitários Tailwind, sem paleta própria. Proposta de primitivas
  Radix para os componentes necessários; compatibilidade deve passar no
  spike de dependências antes de fixar a configuração gerada.
- Componentes iniciais: Button, Input, Textarea, Label, Checkbox, Native
  Select, Dialog/AlertDialog, Table e Alert; adicionar somente os usados.
  Acessibilidade é verificada no fluxo real, não presumida pelo fornecedor.
- TanStack Query usa SDK gerado; erro tipado deve ser convertido em falha
  reconhecida pelo Query, pois o SDK pode retornar `error` sem lançar exceção.
  Usar AbortSignal para cancelar consultas.
- Proposta: `staleTime=0`, `gcTime=0`, refetch ao focar desativado, sem retry
  automático de consultas ou mutações M1. Cache apenas em memória;
  limpar queries/mutations e rascunhos ao perder sessão, e cancelar pendentes.
  Não persistir PII em localStorage, IndexedDB ou URL.
- Chaves incluem geração da sessão, recurso, IDs, filtros, offset e limite.
  Depois de escrita bem-sucedida, invalidar detalhe/lista/relações/histórico
  afetados. Sem atualização otimista que aparente confirmação antes do commit.
- React Hook Form mantém rascunho; resposta refetch não sobrescreve formulário
  dirty. HTTP 409 mantém os valores digitados e oferece comparação/reaplicação
  manual. Não repetir a escrita automaticamente com uma revisão nova.
- Botões distintos: salvar proposta/alteração, confirmar unidade, rejeitar,
  aplicar decisões selecionadas e arquivar. Aceitar importação não confirma.
  Exibir confirmação como confirmação pelo usuário, não certificação externa.
- Data Mode protege navegação interna com alterações pendentes;
  recarregar/fechar aba requer beforeunload separado. Nenhum mecanismo promete
  recuperação de rascunhos após encerramento abrupto.
- CSS da aplicação não deve contaminar os templates de currículo M2.
  Renderer futuro terá documento/escopo próprios para CSS/preflight.

### Backend

| Localização proposta | Componente / interface de aplicação |
| --- | --- |
| `resume_core/career_kb/` | `CareerService`: create, propose_update, apply_update, get, list, archive, link/unlink, history, confirm/reject |
| `resume_core/career_kb/policy.py` | Checar operação/clearance antes de selecionar valores, filtrar campos, fontes e relações |
| `resume_core/career_kb/repository.py` | ORM, projeções SQL autorizadas, snapshots e atualização condicional |
| `resume_core/imports/` | `ImportService`: prepare, candidates, preview_decisions, apply_decisions, undo |
| `resume_core/imports/seed_v01.py` | Schema legado estrito e adapter puro; entrada não altera banco |
| `resume_core/sources/` | SourceService, manifesto de arquivos, armazenamento imutável e leitor limitado de metadados PDF |
| `resume_core/persistence/` | Unit of Work compartilhada: conexão/transação explícita, repositories na mesma transação |
| `resume_api/routers/` | Routers KB/imports/sources; mapeamento de erros, sem regras de confirmação ou merge |

Todos os métodos recebem Principal e requestId. Escritas recebem chave
idempotente e revisões-base aplicáveis. Não aceitar principal, clearance,
capabilities ou paths de disco enviados pelo cliente. ORM não sai dos
repositórios como objeto lazy que um serializer possa explorar.

Serviços síncronos de DB/arquivos executam fora do event loop, com sessão
criada/usada/fechada no mesmo trabalho. Nenhuma sessão SQLAlchemy global.
Preparação continua direta, sem fila; subprocesso limitado de metadados
PDF é uma operação subordinada à requisição, não um job Dramatiq.

## Data Models

### Identidade e estado atual — proposta para aprovação

`kb_entities`: UUID gerado, kind fechado, profile_id quando aplicável,
head_revision_id, privacy, archived_at, created_at e updated_at.
`kind` determina exatamente uma linha na tabela de conteúdo correspondente;
invariantes são verificadas pelo serviço e pela migration onde expressáveis.

Não copiar os IDs legados diretamente como PK canônica. Guardar mapeamento
por fonte, batch e tipo. Um legacyId isolado não autoriza merge entre fontes.

| Tabela tipada / entidade | Campos propostos de conteúdo | Base da proposta |
| --- | --- | --- |
| `kb_profiles` / Profile | full_name, professional_headline, email, phone_original, objective_original, city_of_residence, country_of_residence, linkedin_url, github_url | Campos observados no seed; desconhecidos opcionais |
| `kb_experiences` / Experience | company_name_original, job_title_original, start_date_original, end_date_original, start_period, end_period, end_date_is_current_as_of_source, location | Seed e preservação histórica; períodos normalizados opcionais |
| `kb_statements` / Statement | text_original, text_current, statement_type | Seed e requisito de bullets/versões; tipo fechado proposto responsibility/activity/result/editorial/unspecified |
| `kb_projects` / Project | title, title_is_generated_label, description_original, description_current, time_to_develop_original | Seed; títulos editoriais explícitos |
| `kb_achievements` / Achievement | text_original, text_current, metric_type/value/unit/meaning opcionais | Seed; métrica não é inferida de narrativa |
| `kb_skills` / Skill | name, original_labels, category, explicitly_listed_in_skills_section | Seed; lista/menção não equivale a confirmação |
| `kb_education` / Education | institution, program_original, start/end_date_original, start/end_period opcionais, ongoing_as_of_source_document, currently_ongoing nullable, location, description_original/current | Seed e distinção entre passado e presente |
| `kb_languages` / Language | language, proficiency_original | Seed; sem conversão automática para CEFR ou outra escala |
| `kb_evidence` / Evidence | description, evidence_kind=documentary/manual_note, source_document_id, page/trecho quando aplicáveis | Necessidade do domínio; coleção não existe no seed; requer revisão deste modelo |

Campos de conteúdo exigidos propostos: nome de Profile; empresa/cargo de
Experience; texto de Statement/Achievement; título de Project; nome de Skill;
instituição/programa de Education; idioma/proficiência original de Language;
descrição/origem de Evidence. Datas, localização, métricas e contatos não
são requisitos artificiais para criar um fato. Desconhecido é null;
não preenchê-lo com string vazia ou data atual.

`PartialDate` proposto: texto ISO de precisão ano, ano-mês ou dia completo,
com precisão explícita. Conservar texto de origem em separado. Normalizar
somente entrada inequívoca; sobreposição de períodos gera aviso, não correção
ou bloqueio automático. Não resolver "Atualmente" usando o relógio do sistema.

### Relações propostas

- Profile 1:N entidades profissionais do seu conjunto; suportar mais de um
  Profile sem presumir dados pessoais compartilhados entre eles. O seed
  inicial tem um único Profile; essa contagem não limita o domínio.
- Statement pode se vincular a Experience/Project/Profile/Education;
  Achievement a Experience/Project/Education. Vínculos são explícitos e
  opcionais na criação, sem duplicar a declaração textual.
- Skill N:M Experience/Project; Project pode se vincular a Experience.
- Evidence N:M fatos/unidades do Profile; evidência ausente é estado válido.
- SourceDocument 1:N referências de proveniência. Evidence e referência
  documental são conceitos distintos; não gerar Evidence confirmado a
  partir de cada excerpt importado.

Usar tabela `kb_links` com UUID, tipo de vínculo fechado, duas FKs para
`kb_entities`, unidade de campo opcional para Profile, privacidade e revisão.
Unicidade por endpoints/tipo/unidade ativa; validar combinação de kinds,
Profile e existência. Links têm história própria. Arquivar preserva links;
remover associação cria revisão de desativação. Não usar cascata destrutiva.

### Metadados por campo e revisões

- `kb_field_metadata`: entity_id, field_key permitido pelo DTO, privacy
  opcional mais restritiva, confirmação para unidades do Profile e fontes.
  A classificação efetiva nunca é menos restritiva que a da entidade.
- Demais entidades têm confirmação por entidade; restrição de campo pode
  ocultar parte do conteúdo sem alterar a granularidade da confirmação.
- `kb_revisions`: UUID, entity_id, parent_revision_id, action, responsible,
  timestamp UTC, privacy e confirmação pertinentes.
- `kb_revision_fields`: revision_id, field_key, value JSON escalar/estrutura
  fechada, privacy efetiva e confirmação da unidade. Guardar snapshot completo
  como linhas por campo, permitindo seleção autorizada no histórico.
- `kb_provenance` e equivalente por revisão: source_document_id,
  source_sha256, página, trecho original e field_key opcional. Página é
  1-based externamente; fonte/trecho mantêm sua própria classificação.
- Conteúdo original importado nunca é substituído pelo editado; current é
  estado corrente, original permanece no snapshot/fonte.
- Nova revisão registra alteração e snapshot; mudar somente classificação
  não confirma conteúdo nem transfere aprovação. Edição de conteúdo invalida
  a confirmação da unidade alterada. Undo é nova revisão, não UPDATE do passado.
- Revisões, campos históricos e auditoria não aceitam UPDATE/DELETE no fluxo
  normal; propor triggers SQLite para a imutabilidade, com downgrade explícito.

Projeções atuais selecionam somente colunas autorizadas das tabelas tipadas;
projeções históricas filtram linhas de campos antes de carregar valores.
Não recuperar snapshot JSON completo para filtrá-lo somente em Python.
Proveniência de documento restrito não expõe nome/trecho/raw file a quem
não possui autorização de fonte. A UI pode indicar fonte restrita sem
retornar detalhes não autorizados.

### Staging, propostas e auditoria

| Modelo proposto | Responsabilidade |
| --- | --- |
| `source_documents` | ID imutável, kind=file/manual_note, hash da versão, nome privado, media type, contagem real de páginas, classificação, referência interna de arquivo |
| `import_batches` | Fonte, hash original e hash semântico do seed, schema/adapter version, revisão de staging e estado |
| `import_candidates` | IDs legados escopados, tipo, dados propostos, referências, ambiguidades, matches e estado pending_review/accepted/rejected |
| `career_change_proposals` | Propostas manuais com revisão-base, diff e estado proposed/approved/rejected/applied |
| `review_commits` / items | Decisões selecionadas, snapshots antes/depois, vínculos afetados e conjunto necessário para undo |
| `mutation_receipts` | Principal, operação, chave, hash do comando, resultado original e referências afetadas |
| `kb_audit_events` | Quem, quando, ação, fontes, revisões/commits, requestId; sem depender do log operacional |

JSON de candidatos é privado e validado por união discriminada de DTOs;
nunca é consultado como CareerFact canônico. Aqui JSON representa proposta,
não substitui tabelas tipadas dos fatos aprovados.

Para cadastro manual, propor SourceDocument `manual_note`: anotação explícita
do usuário guardada como fonte privada. Isso não constitui prova externa nem
confirma o fato. Esta é uma proposta de schema/comportamento para revisão,
necessária para cadastrar dados fictícios sem exigir um PDF para cada entrada.

## Import Flow and File Lifecycle

1. UI seleciona PDF e JSON com file inputs; envia os dois arquivos em
   `multipart/form-data` a `POST /api/imports`. Não recebe caminho absoluto.
   Nome de arquivo é apenas metadado privado, nunca caminho de destino.
2. Boundary autentica, checa capability/Origin/Host e aplica limites antes
   de fazer parsing multipart ou criar temporários. Um único preparo ativo
   por processo; contar bytes recebidos mesmo sem Content-Length.
3. Armazenar temporários privados e validar seed `career-kb-import-v0.1`
   estrito, IDs/referências, schema, tamanho, profundidade e campos conhecidos.
   Proibir chaves JSON duplicadas, números não finitos e coerções silenciosas.
4. Verificar assinatura/hash do PDF e metadados com leitor limitado em
   subprocesso. Não extrair texto, executar conteúdo ou acessar anexos/URLs.
   PDF criptografado, ilegível ou fora do limite falha explicitamente.
   Conferir páginas citadas contra a contagem efetiva, não somente a declarada.
5. Calcular hashes dos bytes originais e hash semântico do JSON validado
   para dedup. Chave natural proposta: source hash + seed semântico +
   schema/adapter version. Reformatação JSON não duplica batch.
6. Normalizar apenas estrutura inequívoca. Preservar dados históricos,
   anotações abertas e origem por campo; mensagens de ambiguidade genéricas
   usam IDs opacos, sem aparecer em logs. Envelopes legados não são estados
   canônicos: staged_pending_review mapeia para staging pending_review.
7. Instalar cópias imutáveis, por hash, antes de publicar o batch no banco.
   Escrita temporária, fsync de arquivo, rename seguro e fsync do diretório;
   nunca sobrescrever objeto existente sem conferir integridade.
8. Na transação, criar/reutilizar fonte e persistir batch/candidatos/recibo.
   Mesma proposta retorna o batch original. Seed diferente da mesma fonte
   cria nova proposta com diferenças, não nova identidade do PDF.

Não existe transação ACID conjunta entre filesystem e SQLite. O desenho
prefere arquivo durável antes da referência DB: falha pode deixar órfão
privado, nunca um batch visível apontando para arquivo ainda não instalado.
Limpeza/recuperação é operação local autorizada, com conferência de referências
e manifesto; não remover automaticamente arquivos referenciados nem varrer
conteúdo privado antes da autorização. Testar crashes em cada fronteira.

Fontes imutáveis não são servidas como StaticFiles. Download autorizado
retorna attachment, sem cache, com nome sanitizado; conferir integridade
antes de disponibilizar. Arquivos ausentes/adulterados bloqueiam a operação
dependente e pedem reparo, sem fallback silencioso à pasta externa.

## Review, Concurrency and Undo

Previews não escrevem fatos. Decisão distingue action create/update/link/ignore
e disposition accept/reject; confirmação de veracidade é comando separado.
Update exige diff e revisão-base; link preserva identidade e não sobrescreve
conteúdo do destino. Ignore/reject registram auditoria sem criar fato.

Uma Unit of Work abre transação de escrita SQLite IMMEDIATE. Antes de alterar:
autorizar principal, verificar revisões-base, dependências e idempotência.
Repos compartilham a conexão; não fazem commits independentes. Fazer UPDATE
condicional por head_revision_id e conferir rowcount; não confiar em comparação
feita fora da transação ou somente no version counter automático do ORM.

Aplicar seleção valida todas as decisões, endpoints e revisões afetadas.
As dependências entre candidatos devem estar no conjunto selecionado ou
apontar para entidades já aceitas. Se faltar um pai, a UI mostra o bloqueio;
nenhuma inclusão/aprovação implícita. Persistir alterações, snapshots,
auditoria, decisões e recibo no mesmo commit. Confirmar recibo somente após
commit; perda de resposta é resolvida por replay da mesma chave/comando.

Chave idempotente é escopada por principal/operação. Hash do comando inclui
ordem canônica das decisões, unidades e revisões-base. Mesmo comando retorna
resultado original; divergência retorna 409. Replay requer autorização atual
para as referências do recibo antes de retornar conteúdo. Sem PII no recibo
de erro operacional; referências privadas ficam no banco protegido.

Undo usa reviewCommitId e revisões-base atuais. Para cada entidade/link tocado,
conferir head atual e dependências novas/modificadas desde o commit. Criar
novas revisões restaurando estado anterior; para criação original, arquivar
o registro em vez de apagá-lo. Qualquer bloqueio rejeita toda a seleção.
Confirmação posterior também é mudança relevante; não descartá-la por undo.
Reverter não muda o PDF, o seed, auditoria anterior ou snapshots anteriores.

## API Contracts — Proposed

Os tipos e envelopes restantes foram refinados e aprovados pelo proprietário
em 2026-11-17 às 09:12/09:13 (-03), conforme
[contracts-refinement.md](contracts-refinement.md). Essa definição complementa
os campos e a semântica deste design: metricValue textual preservado,
PartialDate e DTOs concretos de criação/leitura, sem taxonomias ou coerções.

DTOs Pydantic com aliases camelCase, extra=forbid e tipos fechados;
seed usa DTO legado separado com snake_case. Exemplos públicos só fictícios.
Rotas abaixo são propostas para a revisão deste design, não API publicada.

| Método / rota | Contrato / comportamento |
| --- | --- |
| GET `/api/career/{kind}` | ListQuery(offset, limit, sort, archived, confirmation); Page(items, offset, limit, total) filtrada por autorização |
| POST `/api/career/{kind}` | DTO de criação tipado + idempotencyKey; cria unverified e revisão inicial |
| GET `/api/career/{kind}/{id}` | DTO tipado autorizado + revisionId; campos omitidos explicitados como restritos sem valores |
| POST `/api/career/{kind}/{id}/proposals` | Proposta de conteúdo + baseRevisionId + idempotencyKey; não aplica automaticamente |
| POST `/api/career/proposals/{id}/decisions` | Aprovar/aplicar ou rejeitar proposta; revisão-base obrigatória |
| POST `/api/career/{kind}/{id}/confirmations` | Unidade(s) explícita(s), baseRevisionId, idempotencyKey; confirmação auditada |
| POST `/api/career/{kind}/{id}/archive` | baseRevisionId + idempotencyKey; arquivo preserva relações/histórico |
| GET `/api/career/{kind}/{id}/revisions` | Página de metadados autorizados; detalhe/diff seleciona campos permitidos |
| GET `/api/career/{kind}/{id}/revisions/{revisionId}` | Snapshot autorizado; revisão deve pertencer à entidade |
| POST `/api/career/links` | DTO de vínculo + revisões-base dos endpoints + idempotencyKey |
| POST `/api/career/links/{id}/archive` | Desativação versionada com revisão-base do vínculo/endpoints |
| POST `/api/imports` | PDF + seed como arquivos multipart; resultado batchId/revisionId, novo ou replay |
| GET `/api/imports/{id}` e `/candidates` | Metadados/contagens autorizados e página de candidatos privados |
| POST `/api/imports/{id}/preview` | Decisões selecionadas e revisões-base; diff/bloqueios, sem commit |
| POST `/api/imports/{id}/commits` | Mesma seleção validada + idempotencyKey; tudo ou nada |
| POST `/api/imports/{id}/commits/{commitId}/undo` | Seleção, revisões-base atuais, idempotencyKey; tudo ou nada |
| POST `/api/sources/manual-notes` | DTO de anotação humana privada, proposta para cadastro manual |
| GET `/api/sources/{id}` e `/content` | Metadados e download com autorização específica de fonte |

Em `{kind}`, registrar rotas concretas por entidade, com modelos concretos
e operationIds únicos. A notação da tabela resume essas famílias; não é um
endpoint que aceite nome arbitrário de entidade/tabela. Não expor um DTO
`dict[str, Any]` como contrato genérico de escrita.
Rotas estáticas proposals/links precedem parâmetros dinâmicos. DTO de leitura
parcial por privacidade distingue valor desconhecido de campo redigido.

### Fonte manual — contrato aprovado em 2026-11-17 às 08:56 (-03)

`POST /api/sources/manual-notes` recebe somente `text` obrigatório (1 a
8.000 caracteres), `title` opcional (até 256 caracteres, podendo ser null)
e `idempotencyKey` UUID. Aplicar aliases/extra=forbid conforme as convenções
da API. Preservar o texto fornecido, codificado em UTF-8 no SourceStorage
imutável por hash; o título corresponde ao nome privado da fonte.
Persistir hash, referência e media type em `source_documents`, com
`kind=manual_note`, `privacy=confidential` e sem página PDF. A chave é
escopada por principal/operação conforme o protocolo de recibos existente.
A anotação não cria fatos nem confirma qualificações. O DTO não aceita
principal, clearance, paths ou classificação escolhidos pelo cliente.

Erros mantêm envelope `error`, com code/message estáveis, requestId e
fieldErrors opcionais com caminhos permitidos; nunca ecoar input rejeitado.

| Status | Casos propostos |
| --- | --- |
| 401 | Sessão ausente/expirada; cancelar dados da sessão na UI |
| 403 | Operação/capability ou origem não permitida |
| 404 | Referência ausente ou não visível, sem distinguir existência |
| 409 | stale_revision, idempotency_conflict, dependent_changes, missing_candidate_dependency |
| 413 / 415 / 422 | Limite excedido / media type não suportado / DTO, seed ou fonte inválida |
| 429 | Rate limit ou preparo já ativo, Retry-After sem repetir escrita automaticamente |
| 503 | storage_unavailable ou database_busy, sem presumir falha/sucesso após resposta incerta |
| 500 | Erro interno sanitizado com requestId |

UI pode reapresentar erro 422 nos campos, mas nunca faz confirmação automática
após validá-los. Paginação usa sort por created_at e UUID como desempate;
filtros e total consideram somente entidades visíveis. Offset não fornece
snapshot entre páginas; após mutação, invalidar listagem e permitir recarregar.

Refinamento aprovado em 2026-11-17 às 09:32 (-03): filtro de confirmação
do Profile exige `confirmationField` explícito e `confirmation`; os demais
tipos continuam por entidade. O SQL filtra a classificação do campo antes
de selecionar e contar, conforme [contracts-refinement.md](contracts-refinement.md).

## Authorization and Privacy Matrix — Proposed

Separar capability de operação e clearance de conteúdo. Principal local do
bootstrap é proprietário, com permissões KB/import/review/source e acesso
às quatro classificações. Isso não concede capabilities aos perfis M0.5.
Nenhum header/body permite escolher sujeito ou elevar escopo.

| Operação | Capability proposta | Controle adicional |
| --- | --- | --- |
| Listar/ler fatos/revisões | career:read | Classificação de entidade/campo/link; projeção antes dos valores |
| Criar/propor alteração/vínculo/arquivar | career:write | Acesso às entidades/endpoints e revisões-base |
| Aplicar/rejeitar/confirmar/undo | career:review | Unidade explícita, fontes e dependências autorizadas |
| Preparar staging | import:write | Upload privado, limites e principal autorizado antes do parsing |
| Ler staging | import:read | Clearance confidential ou superior para carga inicial |
| Ler fonte/metadados/trecho | source:read | Classificação própria da fonte; liberar fato não libera PDF |

Rebaixamento explícito de classificação é ação auditada, restrita ao
proprietário/reviewer autorizado. Campos podem ser mais restritivos que a
entidade; consultas/diffs não vazam trechos de fontes de classificação maior.
IDs não autorizados recebem resposta indistinguível de ausentes após checagem
de capability. Testes usam principals restritos pela composição de teste;
não criar endpoint de impersonação ou gestão de perfis remoto no M1.

## Budgets — Proposed for Approval

São limites operacionais iniciais, não benchmarks ou metas de performance.
Validar os limites com fixtures de borda e mensagens explícitas.

| Recurso | Limite proposto |
| --- | --- |
| Rotas M0/bootstrap | Preservar orçamento atual de 1 KiB |
| Escrita JSON KB/review | 256 KiB por requisição, contagem de bytes antes do parsing |
| Leitura HTTP KB/review | Até 1 MiB de JSON serializado; não truncar silenciosamente campo ou diff, pedir seleção/página menor se exceder |
| Upload importação | 12 MiB totais; exatamente 1 PDF até 10 MiB e 1 seed até 1 MiB |
| Seed | 1 fonte PDF, até 500 entidades e 2.000 vínculos/referências, profundidade JSON 16 |
| PDF | Até 50 páginas; subprocesso de metadados até 5 s e budget de memória proposto 512 MiB |
| Textos/identificadores | Texto até 8.000 caracteres, nomes 256, IDs legados 128; UUIDs canônicos gerados |
| Lote de decisões/undo | Até 100 itens, além do limite de payload |
| Listagens | Default 25, máximo 100; offset máximo 10.000; sort/filter por whitelist |
| Preparo concorrente | 1 por processo; recusas explícitas, sem criar fila |
| Rate limit | KB: 120 req/min por sessão; import prepare: 5/min por sessão e 10/min global |
| Locks/transação | Espera SQLite atual 250 ms; sem retry automático de escrita após resultado incerto |

O leitor PDF recebe somente bytes/arquivo temporário autorizado, ambiente
filtrado e nomes controlados; saída é metadado mínimo ou erro codificado.
RLIMIT/timeout reduzem consumo, mas não constituem sandbox de segurança
completo. Não usar shell, instalar ferramentas nem afirmar bloqueio de rede
que o runtime não implementa. Logs/warnings do parser nunca são repassados
crus à API ou ao log principal.

## Dependency Proposal and Compatibility Gate

Bibliotecas aprovadas: Tailwind, integração Vite, TanStack Query, React Router,
React Hook Form e componentes shadcn necessários. Proposta de primitivas Radix,
sem acrescentar store global, Zod ou biblioteca de tabela avançada no M1.

| Escolha nova/direta | Motivo | Alternativa e tradeoff |
| --- | --- | --- |
| Declarar `python-multipart` na API | Upload dos dois arquivos por file picker em uma operação; já consta do uv.lock transitivamente | Upload binário em etapas evita multipart, mas aumenta endpoints/estados órfãos; JSON/base64 aumenta payload e memória |
| Adicionar `pypdf` somente ao leitor de metadados | Conferir contagem real de páginas e estrutura sem depender de binário do host | pdfinfo exige ferramenta Linux/CI adicional; confiar somente no manifesto deixa páginas inválidas sem detecção |

`python-multipart` consta do lock como 0.0.33; declará-lo diretamente evita
depender acidentalmente da instalação do pacote MCP. `pypdf` não está no
lock atual e ainda não foi instalado. O uso proposto é
metadado, sem extração de texto, ingestão geral ou renderização de PDF.
Começar com parsing estrito; se o documento real não for aceito, apresentar
o bloqueio e uma proposta, sem alterar a fonte nem mudar silenciosamente
para parsing tolerante. Esta seção é a proposta de dependência exigida
pelas regras do projeto e precisa integrar a aprovação do design.

Antes de fixar versões, executar spike sintético com React/Vite/TypeScript
já pinados, gerar componentes selecionados e passar typecheck/build/formulário
e diálogo por teclado. Não usar `latest` na implementação reproduzível.
Registrar versões exatas, transitivas, lock diff e necessidade de peers.
Sem instalação ou experimento de compatibilidade nesta preparação.

## Migration, CI and Verification

Separar migrations em seams coerentes: entidades/metadados; relações/revisões;
fontes/staging/commits/recibos. Cada upgrade/downgrade preserva tabelas M0 e
conteúdo alheio. Habilitar PRAGMA foreign_keys=ON em cada conexão, incluindo
migrações. Validar constraints e interdição de alteração de histórico por
SQL direto em banco sintético. Downgrade com descarte de dados privados não
é operação de rotina autorizada pelo plano; ensaio somente em banco temporário.

CI é primeira entrega de execução. Runner Linux com Python/Node/pnpm/uv
compatíveis com pins, Docker para harness Redis e Chromium instalado para
os testes existentes. Dependências por locks, sem currículos reais, vault,
credenciais de providers ou clientes CLI externos. `just check` continua
gate agregado; manter upload/parser/cache/contrato no escopo dos testes novos.
Executar CI remoto depende de push autorizado; YAML inspecionado não é run.

Cobertura a detalhar em Tasks: DTO/adapter e estados em Pytest; FK/revisões/
concorrência em SQLite real; HTTP com auth pré-parsing e redaction; SDK
gerado consumido em TS; formulários/cache em Vitest; fluxo sintético completo
em Playwright Test. Campos de confirmação Profile e snapshots privados têm
casos adversariais próprios. Testes de browser continuam fora do backend.

Verifier independente e sensor após o piloto sintético antes da carga privada,
e revisão final após qualquer correção posterior. Carga real é demonstração
local humana; relatório contém apenas IDs opacos e resultados agregados.
M1 só é aceito após AC-M1-001/002/003 e revisão humana, mantendo pendências de
conteúdo explícitas. Medir esforço real conforme o template; não reconstruir
tempo histórico sem evidência.

## Risks & Concerns

| Local observado | Risco | Mitigação / gate |
| --- | --- | --- |
| `resume_api/app.py:141` | Principal só tem capabilities de diagnóstico | Composição confiável adiciona operações KB; testes negativos por serviço e HTTP |
| `resume_api/app.py:151` e `:164` | Limite global 1 KiB e JSON-only impedem importação | Política por rota, auth antes de bytes/parser, testes chunked e limites |
| `resume_api/app.py:335` | Deep links não têm fallback SPA | Whitelist de rotas UI, testes de refresh e API 404 sem HTML |
| `resume_core/database.py:51` | Foreign keys não são habilitadas explicitamente | PRAGMA em toda conexão e teste de FK por SQL direto |
| `resume_api/export_openapi.py:11` | Export usa create_app sem serviços | Routers registráveis sem ler banco/arquivos; contratos offline sem efeitos |
| `logging_policy.py:33` e `:57` | Allowlist atual só M0/GET/POST; expansão ingênua pode vazar path/input | Identificadores de rotas estáticos e códigos, sem valores de query/payload |
| `apps/web/src/main.tsx:14` | Bootstrap por fragmento pode conflitar com inicialização do router | Limpar ticket antes de router e testar StrictMode/reload/deep links |
| `apps/web/vite.config.ts:6` e configs Playwright | Seleções atuais podem não executar novos testes | Atualizar seletores e verificar descoberta de arquivos, sem alegar cobertura por existência |
| `tools/web_harness.py:101` | Timeout de worker já observado no histórico, causa não comprovada | Medir e investigar baseline; sem retries que escondam falha |
| Modelo novo com snapshots | JSON integral ou ORM lazy pode recuperar dados além do escopo | Projeções explícitas e linhas históricas filtradas antes de ler valores |
| Filesystem + SQLite | Crash entre instalação de arquivos e commit DB | Manifesto, arquivos antes das referências, recuperação autorizada e fault injection |
| Novas dependências JS/pypdf | Compatibilidade com pins atuais não demonstrada | Spike sintético + locks + build/typecheck; bloquear execução dependente se falhar |
| `docs/architecture/overview.md:28` | Narrativa ainda diz pacote não executável | Sincronizar documentação operacional na implementação sem reabrir requisitos |

## Traceability and Review Gate

| Requisitos | Seções de design |
| --- | --- |
| MONE-01/02 | Migration, CI and Verification |
| MONE-03/04/05/08 | Data Models; relações, metadata e arquivo |
| MONE-06/07/34 | Authorization Matrix; projeções; Boundary; logs |
| MONE-09/10/11/12/13 | Revisões; Review/Concurrency; formulários |
| MONE-14/15/16/17/18/19/20 | Import Flow; adapter; dedup e fontes |
| MONE-21/22/23/24/25/26/27 | Staging; Review/Concurrency; recibos/auditoria |
| MONE-28/29/30/31/32 | Undo; File Lifecycle; UoW e recuperação |
| MONE-33/35/36/37/38 | CI/Verification e esforço |

Revisão concluída antes de Tasks: o proprietário aprovou este design após
a entrevista e a apresentação dos campos/cardinalidades, fonte manual,
Evidence, DTOs/rotas, permissões, budgets, pypdf/upload e componentes.
As versões exatas continuam sujeitas ao spike de compatibilidade aprovado;
nenhuma instalação ou teste de runtime decorreu da preparação documental.

## Research Sources

Consultados em 2026-11-16 após código/documentos, via Context7 e fontes oficiais:

- [React Router modes](https://reactrouter.com/start/modes): Data Mode e separação do Framework Mode.
- [TanStack Query defaults](https://tanstack.com/query/latest/docs/framework/react/guides/important-defaults): refetch, retries e cache exigem configuração explícita para os fluxos de revisão.
- [shadcn/Vite](https://ui.shadcn.com/docs/installation/vite) e [theming](https://ui.shadcn.com/docs/theming): integração e utilitários sem paleta própria.
- [React Hook Form setError](https://react-hook-form.com/docs/useform/seterror): erros de servidor por campo.
- [FastAPI file uploads](https://fastapi.tiangolo.com/tutorial/request-files/): UploadFile e dependência multipart.
- [SQLAlchemy versioning](https://docs.sqlalchemy.org/en/21/orm/versioning.html): limites do version counter automático; [SQLite](https://docs.sqlalchemy.org/en/21/dialects/sqlite.html): foreign keys por conexão.
- [pypdf PdfReader](https://pypdf.readthedocs.io/en/stable/modules/PdfReader.html) e [strict](https://pypdf.readthedocs.io/en/stable/user/robustness.html): páginas/metadados e riscos de parser tolerante.
- [Hey API fetch](https://heyapi.dev/docs/openapi/typescript/clients/fetch): reutilizar o cliente gerado; comportamento efetivo com upload deve ser demonstrado com a versão pinada.

Documentação consultada não comprova compatibilidade com o conjunto de pins
do projeto. Não foram executados testes de runtime, instalação ou prova do
adapter nesta etapa de design.
