# Cliente TypeScript gerado

Escopo: `packages/api-client/**`. Comandos partem da raiz do repositório.

- `openapi.json` e `src/generated/**` são artefatos gerados; não manter DTOs manuais nem corrigir código gerado diretamente.
- Altere modelos/rotas Python para modificar o contrato; preserve nomes JSON, erros tipados e restrições aprovadas.
- Regenere com `just generate` e verifique com `just check-contract`.
- Inclua OpenAPI e SDK regenerados no mesmo incremento da API; revise o diff por mudanças involuntárias ou exposição de campos privados.
- A configuração do gerador pertence a `openapi-ts.config.ts`; mudanças nela exigem conferir determinismo e compatibilidade dos consumidores.
- Testes relacionados ficam em `tests/integration/test_openapi_contract.py`, nos testes HTTP da feature e em `apps/web/tests/client-contract.ts`. Para consumidores afetados, execute também `just check-web`.
