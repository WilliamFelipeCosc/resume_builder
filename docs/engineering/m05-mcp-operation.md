# Operação local do spike MCP M0.5

Este procedimento usa exclusivamente a candidatura fictícia `app-demo`. Não usa
a Career KB, dados profissionais, credenciais de provider ou envio de formulário.
O servidor oferece apenas `get_application_context` e
`report_application_progress` por `stdio`. A compatibilidade com cada CLI e a
conferência humana devem ser comprovadas nas respectivas execuções live.

## Preparação

Na raiz do repositório, instale o workspace já fixado e inicialize explicitamente:

```sh
uv sync --all-packages --locked
just mcp-spike-init
just check-mcp-spike
```

O `init` cria perfis locais `hermes` e `codex`, concede as capacidades
`application_context:read` e `application_progress:write` somente a `app-demo`
e aplica a migração no SQLite dedicado. Uma inicialização posterior verifica os
perfis existentes; ela não recria um perfil inválido silenciosamente. O comando
`serve` não aplica migração. Sob os diretórios XDG, os caminhos terminam em
`resume-builder/mcp-spike`: `config/profiles` no diretório de configuração e
`mcp-spike.sqlite3` no diretório de dados. Diretórios devem ser privados, sem
symlinks, e pertencer ao usuário; perfis devem ter modo `0600`. Confira o ambiente
XDG e mantenha-o igual para `init`, servidor e consulta de relatos.

```sh
just mcp-spike-serve hermes  # processo MCP stdio, sem terminal interativo
just mcp-spike-reports hermes
just mcp-spike-reports codex
just mcp-spike-form          # http://127.0.0.1:8765/
```

`serve` é iniciado pelo cliente MCP, não por uma chamada HTTP. O servidor do
formulário aceita apenas loopback e assets fixos. Interrompa-o com Ctrl-C.
`reports` lista somente relatos do perfil selecionado, não confirmação externa.
Relatos permanecem no banco até limpeza manual. Para revogar um perfil, encerre
os processos em uso e remova manualmente o arquivo correspondente; o processo já
iniciado mantém o perfil carregado. Mesmo UID é a fronteira de confiança.

## Configuração das CLIs

Os trechos abaixo são exemplos sanitizados, não alteram configuração por si só.
Substitua `/CAMINHO/ABSOLUTO/DO/REPOSITORIO` pelo caminho real do checkout, sem
incluir tokens. Use o Python do `.venv` já instalado, sem download na inicialização.
Defina, quando necessário, os quatro valores `XDG_DATA_HOME`, `XDG_CONFIG_HOME`,
`XDG_CACHE_HOME`, `XDG_STATE_HOME` usados no `init` e verifique que a CLI não
repassa segredos desnecessários ao subprocesso. O mecanismo efetivo de ambiente
precisa ser verificado na execução live de cada versão.

Exemplo Hermes, de acordo com a [documentação MCP do Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp):

```yaml
mcp_servers:
  resume-spike:
    command: /CAMINHO/ABSOLUTO/DO/REPOSITORIO/.venv/bin/python
    args: ["-m", "resume_mcp_server", "serve", "--profile", "hermes"]
```

Exemplo Codex, conforme a [documentação oficial de MCP do Codex](https://developers.openai.com/codex/mcp):

```toml
[mcp_servers.resume-spike]
command = "/CAMINHO/ABSOLUTO/DO/REPOSITORIO/.venv/bin/python"
args = ["-m", "resume_mcp_server", "serve", "--profile", "codex"]
```

O inventário local identificou `codex-cli 0.167.1`; confirme novamente a versão
efetivamente usada na sessão. A versão e o funcionamento do Hermes devem ser
registrados na execução real. Consulte a documentação de cada cliente para o
local de configuração e não sobrescreva nem registre configurações pessoais.

## Verificação por cliente

Com o perfil correspondente e a configuração sanitizada instalada no contexto
escolhido para o teste, inicie a CLI real e registre versão e horário. Solicite:

1. Descobrir as duas ferramentas MCP e seus argumentos.
2. Consultar `get_application_context` com `applicationId=app-demo` e comparar o
   resultado com `data/synthetic/mcp-spike/context.json`.
3. Relatar `started` usando `applicationId=app-demo`, uma `executionId` e uma
   `idempotencyKey` sintéticas fixas para a rodada. Conferir `receiptId` e
   `confirmationState=reported_by_agent`.
4. Repetir exatamente o relato e conferir o mesmo `receiptId`. Usar `reports`
   para verificar o registro persistido do perfil.

Registre comandos, versões, resultado por etapa e recibos, sem segredos. Logs de
`stdout` do servidor pertencem ao protocolo MCP; diagnósticos ficam em `stderr`.
Não alegue compatibilidade real a partir de testes com SDK ou mocks. Em caso de
incompatibilidade, registre início, fim, sintomas e diagnóstico, e interrompa a
investigação após até 60 minutos de trabalho ativo por cliente. Tempo aguardando o
proprietário não conta. Troca de cliente ou continuação além do limite exige
reavaliação; não altere provider nem use fallback pago automaticamente.

## Demonstração com proprietário

Depois das duas validações, escolha uma CLI cuja capacidade de navegador próprio
tenha sido verificada. Inicie `just mcp-spike-form` e forneça à CLI apenas a URL,
`applicationId=app-demo` e a instrução de consultar o MCP, preencher os quatro
campos e parar antes de enviar. Não coloque os valores da fixture no prompt.
Solicite o evento `form_filled`; se bloqueado, registre `blocked`. O proprietário
compara visualmente cada campo com a fixture enquanto a página está aberta. Registre
as quatro comparações, a parada sem envio e o recibo separadamente. O relato não
confirma envio nem substitui a conferência humana.
