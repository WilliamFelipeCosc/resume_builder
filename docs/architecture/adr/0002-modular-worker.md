# ADR-002 — Monólito modular + Worker e Redis

**Status:** Accepted | **Escopo:** V1, salvo indicações explícitas de V2

## Contexto

Há operações rápidas (CRUD) e longas (extração, inferência, PDF) com ciclos de vida distintos.

## Decisão

NestJS monólito modular e Worker Node separado usando BullMQ/Redis. pnpm Workspaces+Turborepo. RabbitMQ apenas experimento opcional.

## Consequências

Worker e API têm isolamentos de processos; Redis requer operação local; SQLite permanece fonte de verdade para jobs/checkpoints importantes.

## Alternativas consideradas

Monólito em um processo ou microserviços foram considerados menos adequados.

## Verificação

Job de teste passa com retry/idempotência; API fica responsiva durante tarefas longas.
