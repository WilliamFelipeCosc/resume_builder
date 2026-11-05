# Resume Builder — PROJECT_SOURCE

> **Status:** especificação de produto e arquitetura consolidada a partir da entrevista com o proprietário, em 2026-11-04. **Não representa software já implementado.** Idioma de trabalho: português; nomes de contratos e código em inglês. Fonte autocontida para ChatGPT Project.

## 1. Objetivo e limites

Criar uma aplicação pessoal **local-first no Linux** para manter uma Career Knowledge Base (KB) fundamentada em fatos e evidências; produzir currículos adaptados a vagas remotas/internacionais; importar e analisar anúncios de emprego; gerar respostas fundamentadas; e oferecer esses dados a **agentes CLI externos** via Model Context Protocol (MCP) para preenchimento de candidaturas. O aplicativo também mantém histórico básico de candidaturas.

**Prioridade de produto:** alcançar **M3 o mais cedo possível**: importar vaga por URL/texto/screenshot → extrair requisitos → encontrar evidências → sugerir alterações de currículo com IA → revisão humana → PDF exportado e vinculado à vaga.

**MVP/V1:** usar **Vertical Slices**; as primeiras entregas são mínimas, mas a **V1 completa** inclui todo o escopo aprovado nesta especificação. V2 agrega descoberta de vagas, melhorias no acompanhamento, workflow formal de aprovação pelo MCP e RAG avançado.

## 2. Decisões consolidadas (DECIDED)

| ID | Tema | Decisão |
|---|---|---|
| ADR-001 | Execução | App local em Linux, React + TypeScript/Vite, NestJS API, Node Worker; servidor vinculado ao loopback. Tauri também na V1 completa. |
| ADR-002 | Backend/monorepo | Monólito modular + Worker separado; pnpm Workspaces + Turborepo; Redis + BullMQ para tarefas; RabbitMQ opcional experimental, sem dependência operacional. |
| ADR-003 | Dados | SQLite + Drizzle ORM, files locais; modo WAL, backup consistente, migração de schema, controle de concorrência. |
| ADR-004 | Automação | **MCP-first exclusivamente.** Sem browser agent integrado, sem Playwright como executor da aplicação, sem gerenciador Chrome/CDP no backend. Hermes/Codex/Claude/Kimi/compatíveis executam navegação externamente. |
| ADR-005 | MCP | `stdio` primeiro; Streamable HTTP adicionado antes de concluir V1. Leitura contextual autorizada + reporte de progresso/resultados; workflow de aprovação via MCP é V2. |
| ADR-006 | IA | Camada multi-provider desde início, Hermes padrão quando configurado, OpenAI alternativa manual. Sem fallback automático para API paga. MCP pode oferecer tanto dados quanto `suggest_answer` opcional; agente externo pode usar IA própria. |
| ADR-007 | Privacidade | Classificação público, compartilhável profissionalmente, confidencial, sensível/segredo; importados privados por padrão; aprovação de mudanças de fatos; keyring para segredos e mínimo privilégio. |
| ADR-008 | Recuperação | SQL relacional + FTS5/BM25 primeiro; embeddings e recuperação híbrida completos na V1; pipeline RAG avançado ao final da V2, por aprendizado e benchmarking. |
| ADR-009 | Roadmap | Vertical Slices + spike MCP em M0.5, **M3 acelerado** com currículo adaptado e PDF. |
| ADR-010 | Qualidade | Testes progressivos até V1: unit/integration/E2E, contratos MCP, mocks e AI evals; Quality Gates funcionais e de segurança. |
| ADR-011 | Observabilidade | Pino, OpenTelemetry, Jaeger opcional, auditoria no SQLite, Sentry opt-in e filtrado. |
| ADR-012 | Distribuição | Web local primeiro, Tauri na V1; instalação manual assistida e CLI `doctor`, sem instalar dependências automaticamente. |
| ADR-013 | Documentação | Modular + `PROJECT_SOURCE.md` autocontido + ADRs + `AGENTS.md` independente do agente. |

## 3. Arquitetura lógica

```text
[React/Vite Web] ------+ 
[Tauri Desktop] -------+--> [NestJS API / Application Services] --> [SQLite/Drizzle]
                              |         |                 |--> [Filesystem XDG]
                              |         +---> [Redis/BullMQ] --> [Node Worker]
                              +--> [AI Provider Adapters: Hermes default / OpenAI manual]
                              +--> [CareerContextRetrievalService]
                              +--> [ApplicationContextService + Answer Engine]
                              ^
           [MCP Server: stdio / Streamable HTTP]
                     ^ tools/resources/prompts
        [External CLI agents: Hermes / Codex / Claude Code / Kimi]
                     | own browser tooling / own permissions
                 [Recruitment Web Forms]
```

MCP conecta-se a **Application Services** autenticados, sem acesso irrestrito ao banco. O navegador, as sessões, CAPTCHAs e o envio são de responsabilidade do agente externo e/ou usuário. A aplicação não consegue impedir tecnicamente um clique externo fora do MCP; deve evitar prometer essa garantia.

## 4. Módulos e comportamentos obrigatórios da V1

### 4.1 Career Knowledge Base

- Entidades independentes e relacionadas: `Experience`, `Project`, `Achievement`, `Skill`, `Evidence`, `SourceDocument` e vínculos many-to-many quando pertinentes.
- CRUD estruturado com proveniência, versões, status de confirmação e evidência opcional.
- Ingestão manual/conversacional e importação **PDF, DOCX, MD, TXT, JSON**, diretórios locais selecionados, vault Obsidian local, GitHub repositórios/docs e dados **exportados pelo usuário do LinkedIn** (sem scraping não autorizado); implementação em incrementos na V1.
- Pipeline adapters → normalização → extração/deduplicação → **Staging Area** (`create/update/link/ignore`) → revisão individual/lote → commit com auditoria/undo.
- Conflitos: IA pode recomendar com evidências, mas não sobrescrever silenciosamente fatos confirmados; distinguir confiança na extração de veracidade.

### 4.2 Resume Studio

- `ResumeDocument` estruturado como única fonte semântica, com conteúdo/layout/estilo separados.
- Templates React baseados em componentes: ATS simples e visual; CSS override controlado, sem JS arbitrário de templates na V1.
- Editor híbrido: painéis, edição inline, drag-and-drop de seções/experiências/bullets, preview imediato, zoom, paginação e propriedades visuais.
- Alterações AI como `ChangeSet` tipado, com diff, evidências, aprovação parcial/total, revisões/snapshots, undo/redo e rollback.
- Exportação PDF ATS/visual (Playwright para **renderização/exportação**, não para preencher vagas), DOCX (`docx` JS ou equivalente validado), HTML estático; validar ordem textual, paginação, integridade e legibilidade ATS sem prometer pontuação universal.
- IA no editor progride de ações inline (início) → chat contextual → sugestões disparadas por eventos (todas na V1).

### 4.3 Job Intelligence

- Importar prioritariamente por **URL**, com fallback texto manual e **screenshot/imagem** analisada por provider com visão quando disponível; não exigir navegador integrado para importação.
- Preservar texto/imagem original, URL, origem, timestamp, snapshot/versionamento e metadados; registrar lacunas e incerteza da extração.
- Requisitos separados: obrigatórios, desejáveis, eliminatórios, senioridade, localização/remoto, remuneração quando declarada, tipo de contrato, stack.
- Matching explicável por requisito: evidências encontradas, lacunas, fontes e justificativas; não inventar `ATS score` ou transformar similaridade em prova de qualificação.
- Vincular `JobPosting` e `JobSnapshot` ao currículo adaptado e à candidatura.

### 4.4 Application Answer Engine

- Reutilizar respostas aprovadas e gerar novas respostas fundamentadas por KB/validação; classificar: factual, técnica, comportamental, preferência, elegibilidade/sensível.
- Respostas têm proveniência, estado (`suggested`, `approved`, etc.), revisão seletiva; sem reutilização cega de motivação específica de outra empresa ou dados sensíveis.
- A V1 permite agentes CLI consumirem respostas e sugestões; não inclui workflow formal interativo de aprovações por MCP (V2).

### 4.5 MCP Server / agentes externos

- Aplicação **não controla navegador**; agentes compatíveis operam na própria CLI.
- `stdio` + Streamable HTTP com contratos versionados e testes por cliente.
- Tools/Resources/Prompts para consultar contextos mínimos, currículos, evidências, vagas, respostas aprovadas e pedir sugestão opcional; tools bidirecionais para **relatar** progresso e resultado.
- Escopos restritos, consultas associadas a candidatura, validação em runtime, IDs de idempotência, logs sanitizados e auditoria.
- Sem ferramentas MCP de SQL/shell genérico ou `submit_application`.
- Diferenciar `reported_by_agent`, `confirmed_by_user`, `verified_by_evidence`. Confirmação de envio depende de evidência e/ou humano; V1 não tem aprovação via interface durante execução CLI.

### 4.6 Application Tracking

- Registro de vagas, candidaturas, datas, links, currículo/revisão, respostas usadas, anotações e etapas seletivas atualizadas **manualmente**.
- Eventos MCP podem alimentar histórico operacional; não atualizar automaticamente status externo sem confirmação apropriada.
- Notificações locais, lembretes/follow-ups e integrações e-mail/calendário são V2.

### 4.7 Context Retrieval

- SQL relacional e FTS5/BM25 primeiro, retrieval semântico por embeddings depois; fusão com ranking testado por datasets até concluir V1.
- Embeddings locais preferidos quando viáveis, remoto opcional e autorizado; abstração separa modelo/versão/dimensões; não misturar vetores entre modelos.
- Aplicar escopo de privacidade antes de indexação/consulta/resposta; evidências preservam `sourceId`, trecho, versão e status de confirmação.
- Carregamento progressivo no MCP (resumos e referências; detalhes sob demanda), orçamento de tokens, truncamento explícito e medição de recall/precision/latência/tokens.
- V2 final: query rewriting, query decomposition, reranking, adaptação de estratégias, comparação de embeddings e benchmarks.

## 5. Segurança, consentimento e limites

- Local-first **não significa** ausência de envio de dados: Hermes e providers remotos podem processar dados na nuvem; filtrar por classificação e autorização antes de transmitir.
- Credenciais no keyring Linux (Secret Service quando disponível), senão falha segura/alternativa explicitamente aprovada, nunca em Git/logs.
- API e MCP HTTP somente loopback, autenticação adequada, validação de `Origin`/`Host`, CSRF quando aplicável, mitigação de DNS rebinding, limites de payload e rate limit.
- MCP `stdio`: minimizar credenciais do subprocesso; nada de logs em stdout (reservado ao protocolo), restrição do usuário local e capacidade de cliente.
- Documento de vaga e conteúdo MCP externo são **dados não confiáveis**; rejeitar prompt injection como instrução de sistema.
- Envio final de candidatura: **manual por padrão**, feito no agente externo com sua confirmação; o MCP não controla ações fora dele.
- Sentry: consentimento explícito e filtragem local; sem currículo/prompt/cookie/screenshot/documento bruto por padrão. Eventos auditáveis no SQLite separados de logs de debug.

## 6. Infraestrutura e operação

- pnpm Workspaces + Turborepo. Apps `web`, `api`, `worker`, `mcp-server`, e `desktop` ao final da V1.
- Redis em Docker Compose iniciado manualmente; RabbitMQ apenas profile experimental opcional. API/Worker Node nativos no desenvolvimento; systemd --user opcional na distribuição.
- Dados em diretórios XDG: config `~/.config/...`, data `~/.local/share/...`, cache `~/.cache/...`, state `~/.local/state/...`.
- `resume-agent doctor`: diagnostica dependências e configuração sem instalar/alterar o sistema automaticamente.
- Backups automáticos locais + manuais, verificação de hash, manifesto, retenção, criptografia opcional e restore atômico controlado; exclui keyring, cookies/Chrome profile, cache Redis e traces por padrão.
- Web primeiro; Tauri desktop + RPM para Linux até V1 completa; AppImage opcional sujeito a viabilidade. Instalação **manual assistida**, não wizard que gerencia dependências externas.

## 7. Observabilidade e testes

- Pino JSON, OpenTelemetry traces/métricas, Jaeger opcional, Sentry opt-in; métricas por provider, latência, tokens disponíveis, estimativa de custo quando confiável, aceite de sugestões, erros de extração, jobs e métricas MCP.
- Auditoria de domínio no SQLite por `actor/clientId`, timestamp, `requestId`, `applicationId`, evento e versão; os relatos de agentes não são comprovação automática.
- Vitest unit/integration; Playwright Test para UX e **sites simulados** quando testando agentes externos; testes de contrato `stdio`/HTTP e pelo menos dois clientes CLI; mocks dos providers; AI Evals com datasets versionados; testes de backups, permissões e recuperação.
- CI determinístico; execuções live de Hermes/OpenAI controladas e opt-in. Quality Gates mensuráveis, baselines calibrados com fixtures; nenhum teste com envio de candidaturas reais.

## 8. Roadmap aprovado — prioridade M3

| Marco | Entrega principal | Limite |
|---|---|---|
| **M0** | Foundation mínima: monorepo, API, React, SQLite, Redis/Worker, segurança/testes mínimos | Sem implementar toda infraestrutura avançada |
| **M0.5** | Spike MCP `stdio` com dados fictícios, consulta + reporte; validar dois clientes CLI | Não implementar workflow completo |
| **M1** | Career KB Core: CRUD de experiências, projetos, skills e evidências | Adapters de importação avançados depois |
| **M2** | Resume Core: modelo, template ATS, formulário, preview, PDF e versão inicial | Inline/drag-drop/chat depois |
| **M3** | **Primeira entrega utilizável prioritária**: URL/texto/screenshot → requisitos → matching → tailoring com IA → revisão → PDF | Não depender de MCP completo ou embeddings |
| **M4** | MCP V1 completo: ferramentas bidirecionais, Resources/Prompts, HTTP, controle de acesso e compatibilidade | Sem execução browser interna |
| **M5** | Application Answers + Tracking básico | Sem workflow MCP formal de aprovação |
| **M6** | Completar Career KB, Resume Studio, chat/sugestões, importações, DOCX/HTML e retrieval híbrido | Completar escopo funcional V1 |
| **M7** | Hardening, evals, observabilidade, backups, Tauri/RPM e documentação | V1 concluída só após Quality Gates |

**M3 Done:** importar vaga por URL/texto/imagem (com falhas controladas), extrair requisitos, explicitar gaps, selecionar evidências autorizadas, gerar proposta textual/estrutural sem inventar fatos, revisar alterações, exportar PDF validado, associá-lo à vaga/revisão, coberto por testes essenciais. Recomendação: usar fixtures com IA simulada no CI e um teste real controlado do provider.

## 9. V2 (DEFERRED)

- Descoberta e monitoramento automatizados de vagas.
- Job Tracking com lembretes, follow-ups, notificações e possíveis integrações e-mail/calendário.
- MCP bidirecional com **workflow formal de aprovação**, incluindo aprovações na interface e retomadas de agentes compatíveis (sem alegar controle de ações externas).
- RAG avançado ao final da V2 (objetivo explícito de aprendizado): query rewriting, decomposição, reranking, índices especializados, benchmarks e critérios de custo-benefício.
- Observabilidade/analytics de candidaturas mais profundos, adapters e brokers opcionais; automação em massa não é compromisso assumido.

## 10. Contratos centrais (conceituais, não API final)

```typescript
interface CareerFact { id: string; provenance: string[]; confirmation: 'confirmed'|'unverified'; privacy: 'public'|'professional'|'confidential'|'secret'; }
interface ResumeRevision { id: string; resumeId: string; jobSnapshotId?: string; content: unknown; parentRevisionId?: string; }
interface ChangeSet { id: string; baseRevisionId: string; operations: unknown[]; evidenceIds: string[]; state: 'proposed'|'approved'|'rejected'|'applied'; }
interface ApplicationContext { applicationId: string; jobSnapshotId: string; resumeRevisionId: string; approvedAnswers: unknown[]; evidenceRefs: string[]; restrictions: string[]; }
interface ApplicationReport { applicationId: string; executionId: string; idempotencyKey: string; status: 'in_progress'|'blocked'|'reported_submitted'|'reported_failed'|'unknown'; source: 'external_agent'; }
```

Schemas executáveis e operações MCP serão definidos e validados em `docs/contracts/`, respeitando proveniência, política de privacidade, versões e idempotência.

## 11. Riscos e não objetivos

**Riscos bloqueantes:** compatibilidade CLI/MCP; exposição de dados profissionais; afirmações sem evidência; resultados externos incorretamente marcados como enviados; ingestão de páginas dinâmicas/screenshot; lentidão e duplicação de jobs; consistência backup+files.

**Não objetivos V1:** Browser Agent controlado pelo backend, rastreamento em tempo real de screenshots de Chrome, auto descoberta de vagas, notificações de follow-up, workflow de aprovação via MCP, backend distribuído, RabbitMQ obrigatório, Sentry self-hosted obrigatório, garantia universal de leitura ATS ou de compatibilidade com todos os sites.

## 12. Decisões de implementação em aberto (não bloqueiam a especificação)

- Nome público final do produto e identidade visual.
- Lib do editor inline/drag-and-drop, conjunto final de templates e componente UI.
- Modelo e runtime de embeddings locais; implementação concreta do índice vetorial e método de fusão/rerank, sujeitos a benchmark.
- SDK MCP/versões por cliente e esquema exato de autenticação HTTP/stdio — validar no spike e fixar versões verificadas.
- Integração prática do Hermes como provider de inferência (autenticação e capacidades reais), fluxo vision, limites e termos; sem presunção de uso gratuito ilimitado.
- Estrutura e thresholds definitivos de AI Evals, baseados em corpus de teste e custos medidos.
- Detalhes de empacotamento Tauri, disponibilidade de componentes em distribuições Linux suportadas.

Tais decisões ficam em `docs/decisions/open-decisions.md`, devem ser resolvidas por pequenos spikes/ADRs e nunca silenciosamente elevadas a requisitos aprovados.

## 13. Referência para implementação

- `AGENTS.md`: instruções de execução para assistentes de código.
- `docs/roadmap/milestones.md`: marcos, critérios e sequência detalhada.
- `docs/roadmap/acceptance-criteria.md`: quality gates e traceability.
- `docs/architecture/overview.md` e `docs/architecture/adr/`: arquitetura e decisões.
- `docs/modules/`: especificações funcionais modulares.
- `docs/contracts/`: schemas e operação MCP.
- `docs/references.md`: fontes técnicas oficiais a conferir antes de codificar.

### Regra de interpretação

Se houver conflito entre `PROJECT_SOURCE.md` e uma especificação modular mais recente aprovada, registrar o conflito, aplicar a decisão aprovada mais recente e sincronizar o documento consolidado. Não reabrir decisões DECIDED por suposições técnicas sem apresentar um ADR e obter aprovação.
