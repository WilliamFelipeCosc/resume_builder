# Resume Builder — PROJECT_SOURCE

> **Status:** especificação de produto e arquitetura consolidada a partir da entrevista com o proprietário, em 2026-11-04, e atualizada mediante aprovação explícita em 2026-11-11 (migração para Python/FastAPI, base profissional inicial e template visual) e 2026-11-12 (FastMCP independente e desenho M0.5). **Não representa software já implementado.** Idioma de trabalho: português; nomes de contratos e código em inglês. Fonte autocontida para ChatGPT Project.

## 1. Objetivo e limites

Criar uma aplicação pessoal **local-first no Linux** para manter uma Career Knowledge Base (KB) fundamentada em fatos e evidências; produzir currículos adaptados a vagas remotas/internacionais; importar e analisar anúncios de emprego; gerar respostas fundamentadas; e oferecer esses dados a **agentes CLI externos** via Model Context Protocol (MCP) para preenchimento de candidaturas. O aplicativo também mantém histórico básico de candidaturas.

**Prioridade de produto:** alcançar **M3 o mais cedo possível**: importar vaga por URL/texto/screenshot → extrair requisitos → encontrar evidências → sugerir alterações de currículo com IA → revisão humana → PDF exportado e vinculado à vaga.

**MVP/V1:** usar **Vertical Slices**; as primeiras entregas são mínimas, mas a **V1 completa** inclui todo o escopo aprovado nesta especificação. V2 agrega descoberta de vagas, melhorias no acompanhamento, workflow formal de aprovação pelo MCP e RAG avançado.

**Fluxo mínimo utilizável (M0–M3):** registrar e revisar informações profissionais → montar currículo base no template visual de referência (com alternativa ATS simples) → importar vaga → recuperar fatos e evidências autorizados → propor adaptações com IA → aprovar mudanças → exportar PDF vinculado à vaga e à revisão. Não depender de MCP completo nem de embeddings para concluir M3.

## 2. Decisões consolidadas (DECIDED)

| ID | Tema | Decisão |
|---|---|---|
| ADR-001 | Execução | App local em Linux, React + TypeScript/Vite, FastAPI (Python) e Python Worker; servidor vinculado ao loopback. Tauri também na V1 completa. |
| ADR-002 | Backend/monorepo | Monólito modular + Worker Python separado; pnpm Workspaces (frontend) + uv workspaces (Python) + justfile (comandos); Redis + Dramatiq para tarefas; RabbitMQ opcional experimental, sem dependência operacional. |
| ADR-003 | Dados | SQLite + SQLAlchemy 2 + Alembic, arquivos locais; modo WAL, backup consistente, migração de schema, controle de concorrência. |
| ADR-004 | Automação | **MCP-first exclusivamente.** Sem browser agent integrado, sem Playwright como executor da aplicação, sem gerenciador Chrome/CDP no backend. Hermes/Codex/Claude/Kimi/compatíveis executam navegação externamente. |
| ADR-005 | MCP | `stdio` primeiro; Streamable HTTP adicionado antes de concluir V1. Leitura contextual autorizada + reporte de progresso/resultados; workflow de aprovação via MCP é V2. |
| ADR-006 | IA | Camada multi-provider desde início, Hermes padrão quando configurado, OpenAI alternativa manual. Sem fallback automático para API paga. MCP pode oferecer tanto dados quanto `suggest_answer` opcional; agente externo pode usar IA própria. |
| ADR-007 | Privacidade | Classificação público, compartilhável profissionalmente, confidencial, sensível/segredo; importados privados por padrão; aprovação de mudanças de fatos; keyring para segredos e mínimo privilégio. |
| ADR-008 | Recuperação | SQL relacional + FTS5/BM25 primeiro; embeddings e recuperação híbrida completos na V1; pipeline RAG avançado ao final da V2, por aprendizado e benchmarking. |
| ADR-009 | Roadmap | Vertical Slices + spike MCP em M0.5, **M3 acelerado** com currículo adaptado e PDF. |
| ADR-010 | Qualidade | Testes progressivos até V1: Pytest (backend), Vitest (frontend), Playwright Test (E2E), contratos MCP, mocks e AI evals; Quality Gates funcionais e de segurança. |
| ADR-011 | Observabilidade | structlog em JSON, OpenTelemetry, Jaeger opcional, auditoria no SQLite, Sentry opt-in e filtrado. |
| ADR-012 | Distribuição | Web local primeiro, Tauri na V1; instalação manual assistida e CLI `doctor`, sem instalar dependências automaticamente. |
| ADR-013 | Documentação | Modular + `PROJECT_SOURCE.md` autocontido + ADRs + `AGENTS.md` independente do agente. |
| ADR-014 | Importação inicial da Career KB | `Curriculo.pdf` é o primeiro documento-fonte; dados extraídos e estruturados entram em Staging Area privada, com revisão humana e proveniência antes de persistir fatos confirmados. Seeds não equivalem a banco inicializado. |
| ADR-015 | Template visual | `resume-reference-slate-sidebar-v1`, derivado do PDF fornecido, é o template visual padrão. Preservar template ATS linear como alternativa; conteúdo estruturado independente do layout, com validação de paginação e legibilidade. |
| ADR-016 | Framework MCP | FastMCP independente sobre SDK MCP Python; serviços de aplicação compartilháveis; `stdio` no M0.5 e integração HTTP com FastAPI no M4. Spike validado com Hermes e Codex; HTTP permanece para M4. |

## 3. Arquitetura lógica

```text
[React/Vite Web] ------+
[Tauri Desktop] -------+--> [FastAPI / Python Application Services] --> [SQLite / SQLAlchemy 2]
                                  |           |                 |--> [Filesystem XDG]
                                  |           +--> [Redis / Dramatiq] --> [Python Worker]
                                  +--> [AI Provider Adapters: Hermes default / OpenAI manual]
                                  +--> [CareerContextRetrievalService: SQL + FTS5/BM25]
                                  +--> [ApplicationContextService + Answer Engine]
                                  ^
               [MCP Server Python: stdio / Streamable HTTP]
                                  ^ tools/resources/prompts
            [External CLI agents: Hermes / Codex / Claude Code / Kimi]
                                  | own browser tooling / own permissions
                           [Recruitment Web Forms]
```

Backend, worker e MCP compartilham contratos e serviços de domínio Python conforme escopos autorizados. O frontend consome API REST/OpenAPI, com cliente e tipos TypeScript gerados; migrações de SQLite ficam sob Alembic.

MCP conecta-se a **Application Services** autenticados, sem acesso irrestrito ao banco. O navegador, as sessões, CAPTCHAs e o envio são de responsabilidade do agente externo e/ou usuário. A aplicação não consegue impedir tecnicamente um clique externo fora do MCP; deve evitar prometer essa garantia.

## 4. Módulos e comportamentos obrigatórios da V1

### 4.1 Career Knowledge Base

- Entidades independentes e relacionadas: `Profile`, `Experience`, `Statement`, `Project`, `Achievement`, `Skill`, `Education`, `Language`, `Evidence`, `SourceDocument` e vínculos many-to-many quando pertinentes. `Statement` preserva declarações individuais (ex.: responsabilidades e resultados) e suas referências à fonte.
- CRUD estruturado com proveniência, versões, status de confirmação e evidência opcional.
- Ingestão manual/conversacional e importação **PDF, DOCX, MD, TXT, JSON**, diretórios locais selecionados, vault Obsidian local, GitHub repositórios/docs e dados **exportados pelo usuário do LinkedIn** (sem scraping não autorizado); implementação em incrementos na V1.
- Pipeline adapters → normalização → extração/deduplicação → **Staging Area** (`create/update/link/ignore`) → revisão individual/lote → commit com auditoria/undo.
- Conflitos: IA pode recomendar com evidências, mas não sobrescrever silenciosamente fatos confirmados; distinguir confiança na extração de veracidade.
- **Importação inicial aprovada como requisito:** usar `Curriculo.pdf` como `SourceDocument` da primeira carga, com staging no estado `pending_review`; `career_kb_seed.json` é artefato de preparação, não um banco já preenchido. O conjunto extraído contém 1 perfil, 4 experiências, 12 declarações, 2 formações, 3 idiomas, 10 habilidades listadas explicitamente e 17 termos adicionais (27 entradas normalizadas), 1 projeto com título editorial e 2 realizações. `resume_document_seed.json` define a primeira seleção/ordem de currículo; ambos são sujeitos a revisão antes de confirmar fatos.
- Preservar trechos originais e proveniência por página/versão; não corrigir automaticamente datas sobrepostas, afirmações de proficiência, formação marcada como “Atualmente”, nomes de ferramentas nem cargos. Termos mencionados não equivalem necessariamente a competência confirmada; rótulos editoriais devem ser identificados como tais. Novas informações posteriores são revisões, não sobrescritas da fonte histórica.
- Arquivos de currículo e seeds contendo dados pessoais são **privados por padrão** e não devem ser publicados no repositório, fixtures de CI ou logs. O documento principal referencia os artefatos por função e nome sem incorporar e-mail, telefone ou outros dados pessoais.

### 4.2 Resume Studio

- `ResumeDocument` estruturado como única fonte semântica, com conteúdo/layout/estilo separados.
- Templates React baseados em componentes: `resume-reference-slate-sidebar-v1` como **visual padrão** e ATS simples/linear como **alternativa**; CSS override controlado, sem JS arbitrário de templates na V1. O template padrão segue a referência `Curriculo.pdf`: página original de 595,92 × 924 pt, fundo branco, barra lateral cinza-azulada à direita (`#99A2B3`), linha do tempo à esquerda, títulos em caixa alta, tipografia de corpo Roboto e nome em serifada (usar alternativas legalmente disponíveis quando necessário).
- Editor híbrido: painéis, edição inline, drag-and-drop de seções/experiências/bullets, preview imediato, zoom, paginação e propriedades visuais.
- Alterações AI como `ChangeSet` tipado, com diff, evidências, aprovação parcial/total, revisões/snapshots, undo/redo e rollback.
- Exportação PDF ATS/visual (Playwright **Python + Chromium** para **renderização/exportação**, não para preencher vagas), DOCX (biblioteca Python equivalente validada, ex.: `python-docx`) e HTML estático; validar ordem textual, paginação, integridade e legibilidade ATS sem prometer pontuação universal. O preview React e o PDF compartilham estrutura semântica, tokens de estilo e regras de layout; testar regressão visual contra a referência e paginação dinâmica sem cortes ou sobreposições.
- IA no editor progride de ações inline (início) → chat contextual → sugestões disparadas por eventos (todas na V1).
- Preservar `ResumeDocument` semântico como fonte única e `ResumeRevision`/`ChangeSet` como registros de adaptações aprovadas: a adaptação a uma vaga pode reordenar e reformular conteúdo sustentado por fatos autorizados, sem alterar os fatos originais da KB. O modelo visual deve continuar reconhecível mesmo com conteúdo adaptado; se o espaço crescer, paginar em vez de reduzir indiscriminadamente a legibilidade.

### 4.3 Job Intelligence

- Importar prioritariamente por **URL**, com fallback texto manual e **screenshot/imagem** analisada por provider com visão quando disponível; não exigir navegador integrado para importação.
- Preservar texto/imagem original, URL, origem, timestamp, snapshot/versionamento e metadados; registrar lacunas e incerteza da extração.
- Requisitos separados: obrigatórios, desejáveis, eliminatórios, senioridade, localização/remoto, remuneração quando declarada, tipo de contrato, stack.
- Matching explicável por requisito: evidências encontradas, lacunas, fontes e justificativas; não inventar `ATS score` ou transformar similaridade em prova de qualificação.
- Vincular `JobPosting` e `JobSnapshot` ao currículo adaptado e à candidatura.
- Gerar propostas de tailoring apenas a partir de informações da KB cuja utilização esteja autorizada; fatos da Staging Area não confirmados devem ser explicitamente apresentados para revisão, não promovidos silenciosamente a qualificações comprovadas.

### 4.4 Application Answer Engine

- Reutilizar respostas aprovadas e gerar novas respostas fundamentadas por KB/validação; classificar: factual, técnica, comportamental, preferência, elegibilidade/sensível.
- Respostas têm proveniência, estado (`suggested`, `approved`, etc.), revisão seletiva; sem reutilização cega de motivação específica de outra empresa ou dados sensíveis.
- A V1 permite agentes CLI consumirem respostas e sugestões; não inclui workflow formal interativo de aprovações por MCP (V2).

### 4.5 MCP Server / agentes externos

- Aplicação **não controla navegador**; agentes compatíveis operam na própria CLI.
- FastMCP independente sobre o SDK MCP Python, conforme escolha do proprietário em 2026-11-12 (ADR-016): `stdio` no M0.5 e Streamable HTTP integrado ao FastAPI no M4, com serviços de aplicação compartilháveis e contratos versionados. Validar compatibilidade real com pelo menos dois clientes no spike; resolução de dependências não substitui testes de runtime/clientes.
- Tools/Resources/Prompts para consultar contextos mínimos, currículos, evidências, vagas, respostas aprovadas e pedir sugestão opcional; tools bidirecionais para **relatar** progresso e resultado.
- Escopos restritos, consultas associadas a candidatura, validação em runtime, IDs de idempotência, logs sanitizados e auditoria.
- Sem ferramentas MCP de SQL/shell genérico ou `submit_application`.
- Diferenciar `reported_by_agent`, `confirmed_by_user`, `verified_by_evidence`. Confirmação de envio depende de evidência e/ou humano; V1 não tem aprovação via interface durante execução CLI.

### 4.6 Application Tracking

- Registro de vagas, candidaturas, datas, links, currículo/revisão, respostas usadas, anotações e etapas seletivas atualizadas **manualmente**.
- Eventos MCP podem alimentar histórico operacional; não atualizar automaticamente status externo sem confirmação apropriada.
- Notificações locais, lembretes/follow-ups e integrações e-mail/calendário são V2.

### 4.7 Context Retrieval

- SQL relacional e FTS5/BM25 primeiro, retrieval semântico por embeddings depois; fusão com ranking testado por datasets até concluir V1. A implementação Python pode incorporar bibliotecas especializadas de embeddings e recuperação sem mudar os requisitos de escopo, proveniência ou privacidade.
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
- Tratar PDFs/DOCX/arquivos importados como entrada não confiável: validar tipo real, tamanho, permissões, caminhos, extração e limites de recursos; subprocessos de renderização e processamento Python devem ser executados com privilégio mínimo. A Staging Area e seus arquivos permanecem privados até autorização.
- Envio final de candidatura: **manual por padrão**, feito no agente externo com sua confirmação; o MCP não controla ações fora dele.
- Sentry: consentimento explícito e filtragem local; sem currículo/prompt/cookie/screenshot/documento bruto por padrão. Eventos auditáveis no SQLite separados de logs de debug.

## 6. Infraestrutura e operação

- Monorepo de duas linguagens: `pnpm`/pnpm Workspaces para `apps/web` e cliente TypeScript, `uv`/`pyproject.toml`/`uv.lock` para os componentes Python (`backend/api`, `backend/worker`, `backend/mcp_server`, `backend/core`) e `justfile` para comandos comuns. `apps/desktop` (Tauri) ao final da V1. API REST/OpenAPI com cliente e tipos TypeScript gerados; evitar duplicação manual de schemas entre linguagens.
- Redis em Docker Compose iniciado manualmente; Dramatiq com broker Redis para jobs, retries e workers Python separados; RabbitMQ apenas profile experimental opcional. API/Worker/MCP Python nativos no desenvolvimento, ferramentas Node.js restritas ao frontend e à cadeia de build TypeScript/Tauri; systemd --user opcional na distribuição.
- Dados em diretórios XDG: config `~/.config/...`, data `~/.local/share/...`, cache `~/.cache/...`, state `~/.local/state/...`.
- Organização de referência: `apps/web`, `apps/desktop`, `backend/{api,worker,mcp_server,core,migrations}`, `packages/api-client`, `assets/resume-templates`, `docs` e `data/seeds` (somente fixtures sanitizadas no Git). Os artefatos reais `career_kb_seed.json`, `resume_document_seed.json`, `resume_template_spec.json` e CSS/gerador de referência serão incorporados no local adequado durante implementação; os que contêm dados pessoais ficam em armazenamento privado, nunca em fixtures públicas.
- Migrações Alembic e transações SQLAlchemy 2 controlam evolução de schema; exportação de PDF usa Playwright Python/Chromium sobre HTML/CSS do template. O `justfile` coordena execução, teste, migração, geração de cliente OpenAPI e build, sem instalar dependências sem consentimento.
- `resume-agent doctor`: diagnostica dependências e configuração sem instalar/alterar o sistema automaticamente.
- Backups automáticos locais + manuais, verificação de hash, manifesto, retenção, criptografia opcional e restore atômico controlado; exclui keyring, cookies/Chrome profile, cache Redis e traces por padrão.
- Web primeiro; Tauri desktop + RPM para Linux até V1 completa; AppImage opcional sujeito a viabilidade. Instalação **manual assistida**, não wizard que gerencia dependências externas.

## 7. Observabilidade e testes

- structlog em JSON, OpenTelemetry traces/métricas, Jaeger opcional, Sentry opt-in; métricas por provider, latência, tokens disponíveis, estimativa de custo quando confiável, aceite de sugestões, erros de extração, jobs e métricas MCP.
- Auditoria de domínio no SQLite por `actor/clientId`, timestamp, `requestId`, `applicationId`, evento e versão; os relatos de agentes não são comprovação automática.
- Pytest unit/integration para backend e Dramatiq; Vitest unit/integration para frontend; Playwright Test para UX e **sites simulados** quando testando agentes externos; testes de contrato `stdio`/HTTP e pelo menos dois clientes CLI; mocks dos providers; AI Evals com datasets versionados; testes de backups, permissões e recuperação.
- Testes específicos do MVP: importação idempotente e revisão da Staging Area, deduplicação/proveniência de registros, contratos OpenAPI/Pydantic e tipos TS gerados, diff/aceite de `ChangeSet`, exportação PDF com extração de texto e ordem de leitura, comparação visual do template com o PDF de referência, paginação sem cortes e isolamento de dados pessoais em fixtures/logs.
- CI determinístico; execuções live de Hermes/OpenAI controladas e opt-in. Quality Gates mensuráveis, baselines calibrados com fixtures; nenhum teste com envio de candidaturas reais.

## 8. Roadmap aprovado — prioridade M3

| Marco | Entrega principal | Limite |
|---|---|---|
| **M0** | Foundation mínima: pnpm + uv + justfile, FastAPI, SQLAlchemy 2/Alembic, React, SQLite, Redis/Dramatiq/Worker Python, segurança e Pytest/Vitest mínimos | Sem implementar toda infraestrutura avançada |
| **M0.5** | Spike MCP Python `stdio` com dados fictícios, consulta + reporte; validar dois clientes CLI | Não implementar workflow completo |
| **M1** | Career KB Core: CRUD de perfil, experiências, declarações, projetos, skills, educação, idiomas e evidências; importar seed do currículo por Staging Area com revisão e proveniência | Adapters de importação avançados depois; sem confirmar silenciosamente os dados importados |
| **M2** | Resume Core: `ResumeDocument`, formulário, preview, PDF e revisões básicas; template visual de referência como padrão e template ATS linear alternativo | Inline/drag-drop/chat depois; fidelidade visual e paginação básica testadas |
| **M3** | **Primeira entrega utilizável prioritária**: URL/texto/screenshot → requisitos → matching com fatos revisados → tailoring com IA → aprovação de alterações → PDF com template selecionado e revisão vinculada à vaga | Não depender de MCP completo ou embeddings |
| **M4** | MCP V1 completo: ferramentas bidirecionais, Resources/Prompts, HTTP, controle de acesso e compatibilidade | Sem execução browser interna |
| **M5** | Application Answers + Tracking básico | Sem workflow MCP formal de aprovação |
| **M6** | Completar Career KB, Resume Studio, chat/sugestões, importações, DOCX/HTML e retrieval híbrido | Completar escopo funcional V1 |
| **M7** | Hardening, evals, observabilidade, backups, Tauri/RPM e documentação | V1 concluída só após Quality Gates |

**M3 Done:** importar vaga por URL/texto/imagem (com falhas controladas), extrair requisitos, explicitar gaps, selecionar evidências autorizadas da KB revisada, gerar proposta textual/estrutural sem inventar fatos, aceitar/rejeitar alterações, exportar PDF validado no template visual padrão ou ATS alternativo e associá-lo à vaga/revisão, coberto por testes essenciais de extração, segurança, paginação e legibilidade. Recomendação: usar fixtures com IA simulada no CI e um teste real controlado do provider. O M3 não exige importadores avançados, editor visual completo, MCP completo ou embeddings.

## 9. V2 (DEFERRED)

- Descoberta e monitoramento automatizados de vagas.
- Job Tracking com lembretes, follow-ups, notificações e possíveis integrações e-mail/calendário.
- MCP bidirecional com **workflow formal de aprovação**, incluindo aprovações na interface e retomadas de agentes compatíveis (sem alegar controle de ações externas).
- RAG avançado ao final da V2 (objetivo explícito de aprendizado): query rewriting, decomposição, reranking, índices especializados, benchmarks e critérios de custo-benefício.
- Observabilidade/analytics de candidaturas mais profundos, adapters e brokers opcionais; automação em massa não é compromisso assumido.

## 10. Contratos centrais (conceituais, não API final)

```python
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

class ApiModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

class CareerFact(ApiModel):
    id: str
    provenance: list[str]
    confirmation: Literal["confirmed", "unverified"]
    privacy: Literal["public", "professional", "confidential", "secret"]

class ResumeRevision(ApiModel):
    id: str
    resume_id: str
    job_snapshot_id: str | None = None
    content: Any
    parent_revision_id: str | None = None

class ChangeSet(ApiModel):
    id: str
    base_revision_id: str
    operations: list[Any]
    evidence_ids: list[str]
    state: Literal["proposed", "approved", "rejected", "applied"]

class ApplicationContext(ApiModel):
    application_id: str
    job_snapshot_id: str
    resume_revision_id: str
    approved_answers: list[Any]
    evidence_refs: list[str]
    restrictions: list[str]

class ApplicationReport(ApiModel):
    application_id: str
    execution_id: str
    idempotency_key: str
    status: Literal["in_progress", "blocked", "reported_submitted", "reported_failed", "unknown"]
    source: Literal["external_agent"] = "external_agent"
```

Os exemplos Pydantic acima são **conceituais**, não schemas definitivos; `alias_generator=to_camel` preserva nomes JSON/TypeScript como `applicationId`, `jobSnapshotId` e `evidenceIds`. `pending_review` é o estado da **Staging Area**, não uma promoção automática do campo de confirmação de `CareerFact`. Os contratos executáveis serão expostos via OpenAPI e consumidos pelo cliente TypeScript gerado, além dos contratos MCP específicos.

Schemas executáveis e operações MCP serão definidos e validados em `docs/contracts/`, respeitando proveniência, política de privacidade, versões e idempotência.

## 11. Riscos e não objetivos

**Riscos bloqueantes:** compatibilidade CLI/MCP; exposição de dados profissionais; afirmações sem evidência; resultados externos incorretamente marcados como enviados; ingestão de páginas dinâmicas/screenshot; lentidão e duplicação de jobs; consistência backup+files; empacotamento e dependências Python/Chromium no Linux; divergência de contratos OpenAPI entre Python e TypeScript; falhas de fidelidade visual/paginação ou extração de texto do template; importação de currículo pessoal sem revisão.

**Não objetivos V1:** Browser Agent controlado pelo backend, rastreamento em tempo real de screenshots de Chrome, auto descoberta de vagas, notificações de follow-up, workflow de aprovação via MCP, backend distribuído, RabbitMQ obrigatório, Sentry self-hosted obrigatório, garantia universal de leitura ATS ou de compatibilidade com todos os sites.

## 12. Decisões de implementação em aberto (não bloqueiam a especificação)

- Nome público final do produto e identidade visual do aplicativo (distinta do template de currículo já aprovado).
- Lib do editor inline/drag-and-drop, templates **adicionais** e componente UI; o template visual padrão `resume-reference-slate-sidebar-v1` e a alternativa ATS linear já foram definidos.
- Modelo e runtime de embeddings locais; implementação concreta do índice vetorial e método de fusão/rerank, sujeitos a benchmark.
- FastMCP independente escolhido (ADR-016); M0.5 validou FastMCP 4.1.8/SDK 2.3.0 e perfis locais restritos `stdio` com Hermes e Codex. Autorização e transporte HTTP permanecem para M4. O aceite inclui exceção histórica de evidência SPIKE-17 documentada em `.specs/features/m05-mcp-feasibility/historical-exception.md`.
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
- `docs/references.md`: fontes técnicas oficiais a conferir antes de codificar (FastAPI/Pydantic, SQLAlchemy 2/Alembic, uv, Dramatiq/Redis, SDK MCP Python, Playwright Python/Chromium, Pytest, structlog, React/Vite e Tauri).
- `assets/resume-templates/`: especificação, tokens visuais e CSS do template de referência e do template ATS; arquivos privados com dados pessoais não devem ser versionados.
- `docs/modules/career-kb.md` e `docs/modules/resume-studio.md` (a criar/sincronizar): fluxos de importação privada, Staging Area e contrato `ResumeDocument` ↔ template ↔ revisão.
- Artefatos preparados fora do código-fonte: `career_kb_seed.json`, `resume_document_seed.json`, `resume_template_spec.json`, `resume_template.css` e `generate_resume.py`; incorporar apenas conforme classificação de privacidade e compatibilidade da arquitetura Python.

### Regra de interpretação

Se houver conflito entre `PROJECT_SOURCE.md` e uma especificação modular mais recente aprovada, registrar o conflito, aplicar a decisão aprovada mais recente e sincronizar o documento consolidado. Não reabrir decisões DECIDED por suposições técnicas sem apresentar um ADR e obter aprovação.
