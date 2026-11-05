# ADR-009 — Vertical Slices com M3 acelerado

**Status:** Accepted | **Escopo:** V1, salvo indicações explícitas de V2

## Contexto

O usuário prioriza obter logo um currículo adaptado a uma vaga sem esperar toda a V1.

## Decisão

M0 mínimo, spike MCP M0.5, KB Core M1, Resume Core M2, e M3 obrigatório: import URL/texto/imagem, requirements, matching, AI ChangeSet/review e PDF. Funcionalidades restantes até M7.

## Consequências

Primeira entrega útil mais cedo; necessidade de evoluir contratos/infra sem comprometer o fluxo.

## Alternativas consideradas

Foundation-first completo ou browser agent-first foram descartados.

## Verificação

AC-M3-* devem passar antes de declarar M3 concluído; M1/M2 continuam expandindo na V1.
