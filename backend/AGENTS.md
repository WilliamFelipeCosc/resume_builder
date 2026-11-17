# Backend Python

Escopo: `backend/**`; especializações locais também se aplicam. Comandos partem da raiz do repositório. Testes em `tests/` têm guia próprio e não herdam este arquivo.

- `core` contém serviços compartilháveis, políticas e persistência; `api`, `worker` e `mcp_server` adaptam transportes/execução. Preserve o sentido das dependências, sem HTTP ou MCP obrigatório no domínio.
- Use Pydantic nas fronteiras e SQLAlchemy 2/Alembic na persistência. Consulte contratos e migrations existentes antes de alterar campos; decisões faltantes exigem esclarecimento.
- Aplique autorização no serviço e filtre dados pela classificação/finalidade antes de consultar ou transmitir. Logs estruturados não incluem documentos, tokens ou payloads privados.
- Mantenha fato, revisão, auditoria e recibos relacionados na transação apropriada; falhas/retries não podem duplicar eventos ou promover confirmação.
- Migrações da aplicação ficam em `backend/migrations/`; o spike tem banco/migrations próprios. Verifique upgrade, integridade de FKs/constraints e rollback ou plano de reversão; não execute contra dados pessoais para validar mudanças.
- Jobs Dramatiq usam identificadores mínimos, retries limitados e idempotência; SQLite é a fonte persistente de resultados, Redis é operacional.
- Mudanças HTTP/Pydantic exigem `just generate` e `just check-contract`, incluindo OpenAPI/SDK no mesmo incremento. Não corrigir contratos editando o TS gerado.
- Testes relacionados: `tests/unit/`, `tests/integration/`, `tests/smoke/`. Execute os casos da área e os negativos de autorização; gates: `just check-python`, `just lint`, mais os exigidos pela feature.
- Referências: `docs/architecture/`, `docs/contracts/` e spec/design aprovados da feature em `.specs/features/`.
