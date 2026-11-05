# Servidor MCP para agentes CLI externos

**REQ-MCP-001..003 — DECIDED.** O aplicativo fornece informações e serviços; não inicia nem controla browsers. Seus consumidores são agentes CLI externos, sujeitos à interoperabilidade real de cada cliente.

## Transportes

`stdio` implementado primeiro (spike M0.5), Streamable HTTP adicionado até M4; ambos expõem a mesma superfície de ferramentas, schema e regras. O MCP TypeScript SDK v2 atual publica pacote servidor `@modelcontextprotocol/server` e docs de ambos os transportes; verificar release/compatibilidade no desenvolvimento. `stdio` reserva stdout exclusivamente ao JSON-RPC; logs em stderr.

## Ferramentas V1

Ver [contratos MCP](../contracts/mcp-tools.md). Consulta autorizada de contexto, evidências, job snapshot, currículo e respostas; sugestão de resposta via IA opcional; reportes de progresso, impedimentos e resultados de candidatura **relatados pelo agente**. Registrar clientId/executionId/correlationId, hash/versão e idempotência.

## Limites de autoridade

- MCP **não** fornece `submit_application`, shell arbitrário, SQL, credenciais do Chrome, cookies, paths arbitrários ou alteração irrestrita de fatos.
- `report_application_result` cria um evento `reported_by_agent`; não muda silenciosamente `Application.recruitmentStatus` para submetido confirmado.
- Aplicativo não garante impedir envio por agente com browser independente. Instruções de envio manual/aprovação devem ser fornecidas também ao agente/usuário, mas são um contrato operacional, não um sandbox.
- V2: workflow formal de aprovação na interface, com pause/resume quando clientes permitirem, sem promessas de bloquear atos externos.

## Segurança

Escopo por candidatura e tipo de dado, autenticação/capability por cliente, requisições limitadas, reautorização da ação sensível. Para HTTP: loopback, host/origin check, proteção DNS rebinding e autenticação. Para stdio: processo invocado localmente, credenciais de menor privilégio, sem token em args/logs e endpoints restritos. Nunca expor documentos privados por padrão, inclusive por Resources.

## Compatibilidade

M0.5: teste com Hermes e um segundo cliente CLI em formulário fictício (leitura + relatório). M4: matrix stdio/HTTP, Resources/Prompts, schemas, erros, autenticação, dados truncados, cliente desatualizado, duplicação de reporte. Não afirmar suporte prático do Kimi/Claude/etc. sem testes.
