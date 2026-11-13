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

## Verificação do ambiente após correção

Em 2026-11-13, após o commit `6b61c0a`, o cliente real executou `hermes -p
m05-spike mcp test resume-spike` com uma variável sentinela fictícia no ambiente
do cliente e na configuração MCP temporária. O cliente conectou via stdio e
descobriu as duas ferramentas com exit 0. Um wrapper de medição efêmero, que
executa em seguida o `tools/mcp-spike-launch` real, registrou somente a presença
da sentinela antes do launcher e seu PID. Um observador local conferiu o mesmo
PID após `exec`, identificou `resume_mcp_server` e comparou os nomes do ambiente
em `/proc/<pid>/environ` à allowlist. Resultado: sentinela presente antes,
ausente depois; os sete nomes observados pertenciam à allowlist. Os valores do
ambiente não foram registrados ou exibidos. O perfil dedicado foi restaurado para
usar diretamente o launcher restrito, sem o wrapper e sem a sentinela.
Os scripts efêmeros usados estão preservados como [wrapper](environment_probe.py)
e [observador](environment_observer.py); o [resultado sanitizado](environment-hermes.json)
contém apenas asserções booleanas e contagem. Os caminhos fixos nos scripts são
os do ambiente desta execução; adapte-os para repetir em outro ambiente.

Uma sessão Hermes adicional consultou contexto e repetiu relato com recibo
`1c8abb5c-0439-4e9e-95f1-f88e4d019afb`, `reported_by_agent`. Como o gateway
preexistente pode ter mantido a conexão anterior, não se atribui essa sessão ao
processo medido no teste de ambiente. A descoberta e o ambiente medido foram
obtidos na mesma execução real de `hermes mcp test`.

## Limite dos tempos de investigação

A transcrição local registra a sessão autenticada inicial de `2026-11-12
19:45:13` a `19:45:34` UTC (diferença entre primeira e última mensagem: 21,15 s)
e a sessão com sucesso de `19:45:50` a `19:46:19` UTC (29,24 s). A repetição
posterior de consulta/relato foi de `2026-11-13 03:58:07` a `03:58:22` UTC
(15,25 s). Esses intervalos não incluem pesquisa, preparação ou esperas. O tempo
ativo total histórico não foi medido; portanto, os registros disponíveis não
comprovam a aplicação do limite total de 60 minutos.
