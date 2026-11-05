# ADR-006 — IA multi-provider sem fallback pago

**Status:** Accepted | **Escopo:** V1, salvo indicações explícitas de V2

## Contexto

Aplicativo precisa de IA para extração, matching, tailoring e respostas; usuário usa Hermes e quer alternativa OpenAI.

## Decisão

Camada multi-provider; Hermes default quando configurado, OpenAI alternativa escolhida manualmente. MCP opcionalmente expõe serviços de IA; executor externo pode usar modelo próprio.

## Consequências

Evita lock-in e chamadas pagas inesperadas; diferenças de capacidade/tokens/vision precisam ser detectadas em runtime.

## Alternativas consideradas

Provider único ou fallback automático para API paga foram descartados.

## Verificação

Testes de provider unavailable, explicit selection, custos e ausência de auto-fallback.
