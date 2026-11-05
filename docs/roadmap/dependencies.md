# Caminho crítico e dependências

## Prioridade absoluta

`M0 foundation mínima -> M0.5 spike MCP (curto) -> M1 KB Core -> M2 CV Core -> M3 job import + tailoring + revisão + PDF`.

M1 precisa fornecer fatos/IDs/proveniência e M2 o documento/export; **não** esperar completar ingestão multi-formato, chat, drag-drop, vetores, Tauri, observabilidade avançada ou aprovação MCP para começar M3.

## Dependências funcionais

- Career KB → ResumeDocument e AnswerEngine.
- JobSnapshot → matching → retrieval autorizado → ChangeSet → ResumeRevision → export.
- ApplicationContextService → MCP tools; MCP não deve conter lógica de domínio duplicada.
- SQLite WorkItems → BullMQ; Redis pode ser reconstruído após restore.
- Privacidade/autorização → toda leitura/IA/MCP/indexação.
- M6 Retrieval híbrido → métricas de qualidade baseadas em M3 SQL+FTS.

## Possíveis paralelismos

MCP spike com dados sintéticos pode acontecer logo após API/contracts mínimos. Design do editor e fixtures de import podem avançar em paralelo. Testes/fuzz de segurança podem acompanhar cada slice.

## Anti-dependências

Não bloquear M3 aguardando RabbitMQ, Grafana, Sentry self-hosted, aprovação remota MCP, automatização de browser integrada, pipeline RAG avançado ou suporte a todas as plataformas de vagas.
