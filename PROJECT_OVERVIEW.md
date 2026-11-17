# Resume Builder — visão geral

Aplicação pessoal local-first no Linux para manter uma Career Knowledge Base fundamentada em evidências, produzir currículos adaptados a vagas e fornecer contexto autorizado a agentes CLI externos via MCP.

## Prioridade e escopo

A primeira entrega utilizável prioritária é **M3**: informações profissionais revisadas → currículo base → importação de vaga por URL/texto/imagem → propostas de adaptação → revisão humana → PDF vinculado à vaga e à revisão.

O escopo completo de V1 permanece na documentação modular: KB e importações, Resume Studio, vagas, respostas/tracking, MCP `stdio`/HTTP, recuperação híbrida, backups, qualidade e distribuição Web/Tauri/RPM. Descoberta automática de vagas, follow-ups, aprovação formal via MCP e RAG avançado ficam na V2.

## Arquitetura e limites

React/TypeScript com Vite; FastAPI; SQLAlchemy 2/Alembic e SQLite; Dramatiq/Redis; pnpm workspaces, uv workspaces e just.

Informações profissionais exigem proveniência e revisão apropriada. Dados privados não pertencem ao Git nem às fixtures de CI. O navegador de candidaturas pertence ao agente externo; a aplicação não oferece executor integrado nem ferramenta MCP de submissão. Providers são escolhidos explicitamente, sem fallback automático para API paga.

## Onde consultar

- [AGENTS.md](AGENTS.md): regras de trabalho e navegação local.
- [Índice e autoridade documental](docs/README.md): fontes e precedência.
- [Requisitos](docs/product/requirements.md), [escopo](docs/product/scope.md), [módulos](docs/modules/) e [contratos](docs/contracts/): comportamento aprovado e propostas identificadas.
- [Roadmap](docs/roadmap/milestones.md), [aceite](docs/roadmap/acceptance-criteria.md) e [ADRs](docs/architecture/adr/): sequência, gates e decisões.
- [Estado dos marcos](docs/process/milestone-status.json) e [execução](.specs/STATE.md): estado canônico e ponte para evidências atuais.

Este resumo orienta; não substitui requisitos e decisões aprovados nem comprova implementação.

## Proveniência

O projeto começou com um pacote de especificações e referências, evoluído por decisões aprovadas. Parte da documentação foi elaborada a partir da especificação consolidada; isso não representa recuperação literal de documentos anteriores nem comprova implementação.

Os documentos completos originais foram arquivados fora do repositório. A [migração documental de 2026-11-17](docs/process/documentation-migration-2026-11-17.md) registra preservação e rastreabilidade; [docs/history/](docs/history/) e os registros de importação preservam a proveniência histórica. O Obsidian mantém resumos sincronizados com as fontes do repositório.
