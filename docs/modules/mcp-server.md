# MCP Server e agentes externos

**M0.5 spike, M4 full.** Framework independente **FastMCP** sobre SDK MCP Python,
escolhido pelo proprietário; ver [ADR-016](../architecture/adr/ADR-016.md).
M0.5 validou FastMCP 4.1.8 com SDK 2.3.0 e clientes Hermes e Codex em `stdio`,
com dados sintéticos e [exceção histórica documentada](../../.specs/features/m05-mcp-feasibility/historical-exception.md).
Serviços Python diretos no M0.5;
montagem HTTP no FastAPI no M4.

## Princípios inegociáveis

MCP-first **sem** navegador integrado. O agente externo controla browser, sessões e envio, com permissões próprias; aplicação não garante impedir ações fora do MCP. MCP oferece dados/contexto mínimo, sugestões opcionais e reportes; não expõe shell, SQL genérico, arquivos arbitrários nem `submit_application`.

## Transportes

`stdio` no M0.5: stdout exclusivamente JSON-RPC/MCP; logs stderr, processo com capabilities limitadas. Streamable HTTP em M4, só loopback com auth/Host/Origin/CSRF quando aplicável e proteção de rebinding. O catálogo de ferramentas deve comportar ambos; contratos versionados e compatibilidade em pelo menos dois clientes CLI.

## Ferramentas

Ler `docs/contracts/mcp-tools.md` para catálogo completo. Em M0.5 basta fake `get_application_context` e `report_application_progress`; em M4 entram context, evidências, currículo, requisitos, respostas aprovadas, suggestions e reportes. Inputs restritos a applicationId/jobSnapshotId e capacidades autorizadas; carregamento progressivo.

## Estado reportado

`reported_submitted` ≠ `confirmed_by_user` ≠ `verified_by_evidence`; replay com idempotencyKey não duplica evento. Reportes são gravação de progresso, sem workflow formal de aprovação/retomada via MCP (V2).

## Validação

Contrato dos tools/resources/prompts, errors tipados, versions, limite payload/tokens, PII leakage, tratamento de prompt injection, falhas de provider e cross-client tests. Formulário fake conduzido apenas pelo agente externo em M0.5.
