# Demonstração externa — M0.5

**Status: conferência visual confirmada pelo proprietário.** O relato do agente é
separado da conferência e não confirma submissão.

- Cliente Hermes Agent v0.23.1, perfil `m05-spike`, servidor MCP stdio com perfil
  `hermes`, dados e candidatura sintéticos `app-demo`.
- O operador iniciou o formulário em `http://127.0.0.1:8765/` e instruiu o
  cliente a consultar o contexto MCP. Os valores da fixture não foram passados
  no prompt.
- A sessão Hermes `local-0a74c01c995aca83e686b5f0a9ba376f85c5c925bbabae115ab8b5b229114d2e`
  chamou `get_application_context` e depois `browser_exec` do próprio cliente.
  A leitura técnica da página pela ferramenta mostrou os quatro valores da
  fixture em `fullName`, `email`, `targetRole` e `approvedAnswer`.
- A sessão não utilizou tool MCP genérica de shell. O Hermes exige o toolset
  `terminal` para disponibilizar `browser_exec`, pois este executa Python no host;
  o prompt proibiu chamadas de terminal e o transcript não registra chamadas
  dessa ferramenta. Aprovações não foram desativadas.
- Hermes relatou que a página permaneceu aberta e não enviou o formulário. O
  recibo persistido `b71a5f51-f706-4856-a193-c678ea82c6cc`, evento `form_filled`,
  `confirmationState=reported_by_agent`, corresponde à execução
  `hermes-form-004` e à chave `hermes-form-key-004`.

## Conferência pelo proprietário

Comparar os campos visíveis com `data/synthetic/mcp-spike/context.json` enquanto
a página estiver aberta. A leitura técnica acima não substitui esta conferência.

- [x] Nome completo corresponde à fixture.
- [x] E-mail corresponde à fixture.
- [x] Cargo pretendido corresponde à fixture.
- [x] Resposta profissional corresponde à fixture.
- [x] A demonstração parou sem envio.

O proprietário confirmou visualmente as quatro correspondências e a ausência de
envio na conversa de execução em 2026-11-12, America/Sao_Paulo. A confirmação é
um relato do proprietário e não substitui o recibo do agente.

## Diagnóstico

Três tentativas anteriores não apresentaram `browser_exec` ao cliente. As duas
primeiras selecionaram `browser`; a terceira incluiu também `browser-use`. Cada
uma relatou `blocked`, sem preencher ou enviar. A inspeção do código instalado
mostrou que `browser_exec` só é oferecida quando `terminal` também está
disponível. A quarta sessão habilitou esse toolset e executou o navegador.
O navegador foi configurado como visível no perfil dedicado; o proprietário
confirmou a inspeção dos valores na conversa.
