# Contratos MCP — rascunho V1

**Status:** catálogo V1 `PROPOSED` na assinatura exata; responsabilidades `DECIDED`.
Para as duas tools do M0.5, o [desenho aprovado](../../.specs/features/m05-mcp-feasibility/design.md)
define o recorte `m05.v1` implementado no spike. Framework escolhido: FastMCP
independente sobre SDK MCP Python, conforme [ADR-016](../architecture/adr/ADR-016.md).
Schemas executáveis e compatibilidade `stdio` com Hermes e Codex foram validados
no recorte sintético; o catálogo V1 completo e HTTP continuam futuros. Veja a
[verificação independente](../../.specs/features/m05-mcp-feasibility/validation.md).

## Convenções

- Entradas contêm `applicationId` ou `jobSnapshotId` explícito; nenhuma busca geral implícita por toda a KB privada.
- Respostas contêm `{schemaVersion, data, provenance, truncated, policy, requestId}` ou erro tipado.
- Limites de paginação e payload obrigatórios. Campos secretos jamais devolvidos sem autorização explícita por finalidade.
- ID de execução externo e `idempotencyKey` em operações de escrita; reporte repetido deve ser no-op idempotente.
- Tool names abaixo são nomes candidatos; não afirmar que já são implementados.

## Tools V1

| Tool | Input resumido | Output / regras |
|---|---|---|
| `get_server_capabilities` | `{}` | schema/transport, permissões efetivas, limites |
| `get_application_context` | `{applicationId, scope?, maxItems?}` | job snapshot, currículo, respostas/evidências autorizadas; progressive loading |
| `get_job_requirements` | `{jobSnapshotId, page?}` | requisitos classificados com IDs |
| `get_career_context` | `{applicationId, query?, evidenceIds?}` | fatos/evidências filtrados por policy |
| `get_evidence` | `{applicationId, evidenceId}` | fonte, trecho, status; somente autorizado |
| `get_resume` | `{applicationId, revisionId?}` | estrutura/resumo e link permitido para export |
| `get_approved_answers` | `{applicationId, questionIntent?}` | respostas reutilizáveis compatíveis |
| `suggest_answer` | `{applicationId, question, questionType?}` | resposta sugerida, evidências, desconhecidos, revisão; provider ativo; pode ser job assíncrono |
| `report_application_progress` | `{applicationId, executionId, idempotencyKey, event}` | evento registrado como relato, receiptId |
| `report_application_result` | `{applicationId, executionId, idempotencyKey, status, evidence?}` | relato, não submissão verificada |
| `health_check` | `{}` | estado MCP/dependências sem revelar segredos |

## Resources e Prompts

Resources: instrução geral sem dados pessoais; dados de uma vaga/revisão sob URI/capability limitada; anexos somente se policy permitir. Prompts: `prepare_application`, `review_before_submission`, `report_outcome`; não confiar em prompts como mecanismo técnico de impedir ações no browser.

## Exemplo: relato seguro

```json
{
  "applicationId": "app-demo",
  "executionId": "exec-demo",
  "idempotencyKey": "exec-demo:event-4",
  "status": "reported_submitted",
  "evidence": { "type": "confirmation_reference", "reference": "DEMO-123" }
}
```

Persistir `reportingSource=external_agent`, `confirmationState=reported_by_agent` e a evidência sanitizada. Conferir se `status` é consistente com tipos permitidos; `reported_submitted` não implica `verified_by_evidence`.

## Erros

`NOT_AUTHORIZED`, `CONTEXT_NOT_FOUND`, `SCHEMA_INVALID`, `CONTEXT_TRUNCATED`, `PROVIDER_UNAVAILABLE`, `REVIEW_REQUIRED`, `RATE_LIMITED`, `CONFLICT`, `REPLAY_DETECTED`, `TEMPORARILY_UNAVAILABLE`. Não retornar secrets em mensagens de erro.

## Transportes

- `stdio`: FastMCP independente sobre SDK Python, sem mensagens fora do protocolo em stdout (logs structlog em stderr); processo por conexão.
- HTTP: endpoint no loopback, auth/capabilities, Origin/Host e DNS rebinding check, rate limit, CSRF se aplicável, limites de sessão.
- Usar mesmo catálogo de ferramentas e schemas gerados/validados em Python nos dois transportes, com testes cruzados e versionamento explícito.

## Critérios e implementação Python

- Registrar schema/capability version na resposta `get_server_capabilities`; o catálogo exato será congelado após o spike M0.5 e testes com duas CLIs.
- `report_application_result.status` deve obedecer a `ApplicationReport.status` em `PROJECT_SOURCE.md` (`in_progress|blocked|reported_submitted|reported_failed|unknown`), sem extrapolar confirmação.
- Distinção entre evento operacional (`report_application_progress`) e resultado (`report_application_result`) deve ser preservada em auditoria.
- `suggest_answer` usa adaptador de provider configurado explicitamente; erros seguros e opção de cliente usar modelo próprio.
- Evitar expor URL/file path de documento sem autorização para finalidade e escopo corretos.
