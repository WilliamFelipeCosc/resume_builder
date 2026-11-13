# Compatibilidade real Codex — M0.5

**Resultado:** descoberta, consulta, relato e replay passaram com dados sintéticos.
A demonstração do formulário e a conferência humana permanecem pendentes.

- Cliente `codex-cli 0.167.1`; modelo configurado no ambiente `gpt-6.1-terra`,
  provider padrão existente. Servidor FastMCP 4.1.8 e MCP SDK 2.3.0 do workspace.
- Sessão `codex exec` efêmera, `--ignore-user-config`, diretório de trabalho
  temporário e sandbox `workspace-write`. Configuração do servidor por `-c`, sem
  editar a configuração global; Python da `.venv`, `--profile codex` e variáveis
  XDG do banco sintético isolado.
- As duas tools do servidor receberam `approval_mode = "approve"` individualmente
  para esta sessão. Não houve bypass global de sandbox ou aprovações. Consulte a
  [documentação oficial Codex MCP](https://developers.openai.com/codex/mcp).

## Evidência

O fluxo `codex exec --json` identificou `resume_spike` e produziu eventos
`mcp_tool_call` completos para as duas ferramentas:

1. `get_application_context` recebeu `applicationId=app-demo`; a resposta
   `data` correspondeu à fixture sintética versionada, com os quatro valores,
   referências, restrições e `policy.clientId=codex`.
2. `report_application_progress` recebeu `applicationId=app-demo`,
   `executionId=codex-live-001`, `idempotencyKey=codex-live-key-001`,
   `event=started`. A chamada repetida usou os mesmos quatro argumentos.
3. Ambas retornaram `receiptId=525fb79e-5351-4916-9fdc-b2cf57523a3b` e
   `confirmationState=reported_by_agent`, com `requestId` distintos.
4. `reports --profile codex` nos mesmos diretórios XDG confirmou uma única linha
   persistida com recibo, cliente, IDs e evento. O `created_at` UTC registrado foi
   `2026-11-13T01:20:16.908551Z`.

O resultado de descoberta foi observado nas chamadas reais emitidas pela CLI,
não inferido do SDK ou de mock. A sessão terminou com exit 0. A resposta de
progresso é relato do agente, sem confirmação de envio. Os testes automatizados
T10/T11 verificam separadamente a sanitização dos streams.

## Diagnóstico

Na primeira tentativa, Codex descobriu as ferramentas, mas rejeitou suas chamadas
porque o modo não interativo usava política de aprovação `never`. Uma segunda
sessão com aprovação restrita às duas ferramentas acima executou as três chamadas.
Nenhum provider foi trocado, nenhuma configuração global foi escrita e nenhum
formulário foi enviado.
