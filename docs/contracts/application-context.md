# ApplicationContext e ApplicationReport

Referência definitiva para campos mínimos: `PROJECT_SOURCE.md` §10. Estes JSONs são exemplos sintéticos.

```json
{
  "applicationId":"app-demo",
  "jobSnapshotId":"snapshot-demo",
  "resumeRevisionId":"revision-demo",
  "approvedAnswers":[],
  "evidenceRefs":[],
  "restrictions":["do_not_submit_without_user_review"]
}
```

Dados são filtrados por finalidade/capability; parte confidencial/secret é omitida sem aprovação. Campos `truncated` e `requestId` pertencem ao envelope MCP quando apropriado.

```json
{
  "applicationId":"app-demo",
  "executionId":"execution-demo",
  "idempotencyKey":"execution-demo:result:1",
  "status":"reported_submitted",
  "source":"external_agent"
}
```

Status permitidos: `in_progress|blocked|reported_submitted|reported_failed|unknown`. A presença de `reported_submitted` **não** muda confirmação para `verified_by_evidence` nem `confirmed_by_user`. Logs e auditoria guardam reportes, confirmação humana e evidências separadamente.

`source=external_agent` é obrigatório para esse contrato; testes devem cobrir replay de idempotencyKey, requestIds cruzados, mudança de status não autorizada e claims sem evidência.
