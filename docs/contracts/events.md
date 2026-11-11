# Eventos, jobs e idempotência

## Auditoria de domínio

Envelope conceitual:

```json
{"eventId":"event-demo","requestId":"req-demo","actor":"user|external_agent|system","clientId":"cli-demo","entityId":"app-demo","eventType":"application.reported","occurredAt":"2026-11-11T12:00:00-03:00","entityVersion":1}
```

Identificar ator, escopo e versão em eventos de importação, revisão, resume changes, job import e reportes MCP. O log de auditoria no SQLite é distinto do structlog de diagnóstico.

## Trabalho Dramatiq

Jobs candidatos: `source_import`, `job_extract`, `tailoring_suggestion`, `pdf_render`, `embedding_index` (M6). Inputs transportam IDs opacos e pequenos, não PDF/PII em payload Redis quando evitável. Persistir estado no SQLite, retries idempotentes com key única e erros estruturados sanitizados.

## Estado da candidatura

Eventos `application.reported_progress` e `application.reported_result` são relatos por agentes externos. `application.confirmed_by_user` exige ação humana; `application.verified_by_evidence` exige regra/avaliação separada. Repetição idêntica da mesma chave não duplica evento; reuso com payload diferente falha por conflito.

## Falhas

Timeout, retries, fila offline, erro de provider, erro de PDF e conflito SQLite são observáveis; não gerar falsa conclusão de exportação/sucesso. Testar recuperação de worker após interrupção.
