# Adapter MCP

Escopo: `backend/mcp_server/**`, em conjunto com `backend/AGENTS.md`. Comandos partem da raiz.

- Consulte `docs/modules/mcp-server.md`, `docs/contracts/mcp-tools.md` e ADR-016; para o spike, `.specs/features/m05-mcp-feasibility/` define o contrato restrito implementado.
- Preserve o recorte sintético do M0.5; o catálogo completo e o transporte HTTP pertencem ao M4. Não anuncie sua implementação a partir do spike.
- `stdout` é exclusivamente protocolo MCP/JSON-RPC; logs e diagnósticos vão para `stderr`, inclusive em falhas de inicialização.
- O adapter chama serviços autorizados; parâmetros não podem ampliar identidade, candidatura ou capabilities concedidas pelo perfil. Não expor shell, SQL ou filesystem genéricos.
- Valide limites, extras, IDs e idempotência; replay retorna o recibo original, conteúdo divergente gera conflito e o recibo só é confirmado após commit.
- Relatos não comprovam submissão. O formulário fictício é demonstrador; navegador e envio continuam sob o agente externo/usuário.
- Banco e migrations do spike são isolados do banco da aplicação; preserve o isolamento no launcher e nos testes.
- Verifique `tests/unit/mcp_spike/`, `tests/integration/mcp_spike/` e os smoke tests MCP via `just check-mcp-spike`; use `just lint` e os gates adicionais exigidos.
- Compatibilidade exige evidência real em Hermes e outro cliente, identificando versões/limitações. Mocks ou uma alteração documental não substituem essa validação.
