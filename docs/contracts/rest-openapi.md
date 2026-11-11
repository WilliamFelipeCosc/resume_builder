# Contrato REST/OpenAPI — fronteira Python ↔ TypeScript

**Decisão:** FastAPI + modelos Pydantic; documentação/esquemas OpenAPI e geração de cliente TS. Rotas listadas abaixo são propostas, não API executando.

## Convenções

- `snake_case` em Python, `camelCase` exposto em JSON (via aliases em Pydantic); `schemaVersion` para envelopes versionados quando necessário.
- IDs opacos, paginação explícita, requestId, erros tipados e limites de tamanho; OpenAPI é fonte de contratos TS gerados.
- Headers/cookies e origin/host/CSRF conforme política; endpoints nunca revelam credenciais ou PDFs privados indiscriminadamente.

## Endpoints candidatos por milestone

| Marco | Recurso | Exemplos de operação |
|---|---|---|
| M0 | Health / features | `GET /api/health`, versão/estado mínimo |
| M1 | Career KB | CRUD entidades; `POST /api/imports`; decisions/commit staging |
| M2 | Resume | CRUD semântico; preview/export; revisions |
| M3 | Jobs | importar URL/texto/imagem; snapshots, requirements, matching |
| M3 | Tailoring | criar ChangeSet, aprovar operações, gerar ResumeRevision/PDF |
| M5 | Applications | CRUD tracking e respostas aprovadas |

Resolver naming de endpoints, schemas de erro, paginação e auth exatos com testes de contrato no momento da implementação. Não tratar a tabela como API publicada.

## Check de integridade

Testes CI devem verificar mudança de schema Pydantic/JSON não deixa cliente TS desatualizado. Dados secretos nunca entram em schema público por acidente. Documentação auto-gerada acessível apenas pelo bind/autorização local apropriado.
