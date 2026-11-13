# Compatibilidade real Hermes — M0.5

**Resultado:** descoberta, consulta, relato e replay passaram com dados sintéticos.
O aceite do formulário e a compatibilidade Codex permanecem pendentes.

- Cliente: Hermes Agent v0.23.1, Python 3.14.9. Provider existente
  `openai-codex`, modelo `gpt-6-luna`; nenhum fallback foi configurado.
- Servidor: FastMCP 4.1.8 e MCP SDK 2.3.0 do workspace fixado.
- Perfil Hermes dedicado `m05-spike`, criado sem clonar credenciais ou skills;
  herança de autenticação do perfil padrão via mecanismo do próprio Hermes.
  Os arquivos de configuração do perfil padrão não foram alterados.
- Banco e perfil MCP sintéticos inicializados sob um diretório privado em `/tmp`;
  servidor stdio invocado com Python da `.venv` e `--profile hermes`.
- Configuração da sessão: seção `mcp_servers.resume-spike` do runbook, com
  variáveis XDG do ambiente sintético. Não registrar segredos ou tokens.

## Evidência

1. `hermes mcp test resume-spike` no ambiente isolado conectou via stdio, exit 0,
   e listou exatamente `get_application_context` e `report_application_progress`.
   O registro do cliente também expõe helpers MCP genéricos para recursos e
   prompts; eles não são ferramentas publicadas pelo servidor.
2. `hermes -p m05-spike chat --toolsets resume-spike --query-file <prompt>
   --run-budget 180` executou sessão real com o provider escolhido. O prompt
   restringiu a sessão a MCP e aos identificadores sintéticos `app-demo`,
   `hermes-live-001`, `hermes-live-key-001`, evento `started`.
3. O conteúdo da chamada `get_application_context` na transcrição Hermes foi
   comparado integralmente em memória com `data/synthetic/mcp-spike/context.json`:
   campos, referências, restrições e quatro valores coincidiram; `policy.clientId`
   foi `hermes`. O resultado contém somente dados fictícios.
4. Duas chamadas `report_application_progress` idênticas retornaram o mesmo
   recibo `3595a76b-d292-4db9-a95f-6029859ca934` e
   `confirmationState=reported_by_agent`; os `requestId` foram distintos.
   `reports --profile hermes`, com os mesmos diretórios XDG, exibiu uma única
   linha persistida com o mesmo recibo, IDs, evento e cliente. Horário UTC do
   registro: `2026-11-12T19:46:09.861006Z`.

As comparações acima foram feitas sobre a transcrição local da sessão sintética e
o resultado de `reports`, sem copiar a transcrição completa nem credenciais.
O relato não representa confirmação de submissão. A inspeção de logs nesta sessão
não substitui os testes de sanitização automatizados de T10/T11.

## Diagnóstico e limites observados

O launcher no sandbox não conseguiu abrir seu lock externo. A consulta escalonada
da versão ficou aguardando uma busca de atualização remota e foi interrompida após
exibir a versão. O primeiro teste com `HERMES_HOME` independente fez o próprio
launcher preparar dependências em `/tmp`; não houve modificação do perfil global.
Nesse ambiente não havia credencial OAuth, de modo que a primeira sessão falhou
antes de chamar as tools. O perfil dedicado oficial resolveu a autenticação.

Na primeira sessão autenticada as tools chegaram após a resposta do modelo. O log
registrou descoberta do servidor cerca de 24 segundos após o início da sessão;
uma nova sessão, após a descoberta, executou as três chamadas MCP. Não houve
alteração de provider, reparo de instalação, submissão ou validação de navegador.
Os períodos de espera por permissão não são tempo de investigação ativa.
