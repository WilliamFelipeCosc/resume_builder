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

## Verificação do ambiente após correção

Em 2026-11-13, após o commit `6b61c0a`, repetimos `codex exec` com a mesma
configuração isolada e aprovação específica das duas tools. A variável sentinela
fictícia foi adicionada ao ambiente do cliente e à configuração MCP efêmera.
Um wrapper de medição registrou apenas a presença da sentinela antes de executar
o `tools/mcp-spike-launch` real e seu PID. Um observador local identificou o
mesmo PID após `exec` como `resume_mcp_server` e comparou os nomes em
`/proc/<pid>/environ` com a allowlist. Resultado: sentinela presente antes,
ausente depois; os sete nomes observados pertenciam à allowlist. Os valores do
ambiente não foram registrados ou exibidos. A medição e as chamadas pertencem à
mesma sessão real, sem modificar a configuração global do Codex.
Os scripts efêmeros usados estão preservados como [wrapper](environment_probe.py)
e [observador](environment_observer.py); o [resultado sanitizado](environment-codex.json)
contém apenas asserções booleanas e contagem. Os caminhos fixos nos scripts são
os do ambiente desta execução; adapte-os para repetir em outro ambiente.

Essa sessão consultou a fixture e registrou/repetiu o evento `started` com
`codex-env-001` e `codex-env-key-001`. Ambas as respostas devolveram o recibo
`34074414-2409-40aa-96b1-331d10405d2c`, `reported_by_agent`; o recibo foi
encontrado em `reports`, com `created_at=2026-11-13T04:00:32.968944Z`.

## Limite dos tempos de investigação

As marcas UTC de persistência verificáveis foram `2026-11-13T01:20:16.908551Z`
para a primeira sessão bem-sucedida e `2026-11-13T04:00:32.968944Z` para a
repetição após correção. As sessões anteriores eram efêmeras; não foi registrado
o início/fim da investigação ativa nem sua duração total. Não é possível afirmar
a partir dessas marcas se o limite de 60 minutos foi observado.
