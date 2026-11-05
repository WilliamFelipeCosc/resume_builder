# Contratos — Eventos de candidaturas e auditoria

## Estados separados

`recruitmentStatus` é estado humano do funil (saved/applied/interview/...); `externalExecutionStatus` é execução relatada (started/in_progress/blocked/reported_submitted/reported_failed/unknown). Nunca derivar automaticamente um do outro sem regra explícita.

## Evento padronizado (PROPOSED)

```typescript
type ConfirmationState = 'reported_by_agent' | 'confirmed_by_user' | 'verified_by_evidence';
interface ApplicationEvent {
  id: string;
  applicationId: string;
  executionId?: string;
  eventType: string;
  reportingSource: 'external_agent'|'user'|'system';
  confirmationState?: ConfirmationState;
  idempotencyKey?: string;
  occurredAt: string;
  recordedAt: string;
  detailsSanitized: Record<string, unknown>;
}
```

## Regras

- Escritas append-only na API; clientes não sobrescrevem eventos históricos.
- Idempotência única por cliente/executionId/idempotencyKey; ordenar logicamente eventos e tolerar atrasos sem supor monotonicidade perfeita de relógios externos.
- Um agente externo nunca recebe autorização de alterar fato confirmado, marcar submissão como comprovada ou alterar estágio seletivo diretamente.
- Evidências de envio podem ser uma referência, timestamp e prova opcional; validar origem e apresentar ao usuário antes de confirmar.
- Segredos e conteúdos de formulário não são armazenados indiscriminadamente em eventos.
