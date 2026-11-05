# ADR-010 — Testes progressivos e Quality Gates V1

**Status:** Accepted | **Escopo:** V1, salvo indicações explícitas de V2

## Contexto

Integração de LLMs e CLIs é probabilística; segurança e portabilidade não podem depender só de demos.

## Decisão

Testes unitários/integração/E2E, mocks e evals, contratos MCP, segurança e restore; iniciar simples e expandir até V1; CI determinístico e live eval controlado.

## Consequências

Ganho de confiabilidade com custo de testes e fixtures; thresholds IA definidos por baseline, não arbitrários.

## Alternativas consideradas

Aceitação apenas funcional ou benchmarking extremo obrigatório foram descartados.

## Verificação

Checklist AC-M7 e evidência de rodadas de testes reais/simulados em releases.
