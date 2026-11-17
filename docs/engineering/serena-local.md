# Serena no ambiente local

O Serena usa LSP para navegação e diagnósticos; os resultados não substituem testes nem revisão. Leia `AGENTS.md` e os guias locais. O índice CodeGraph e buscas textuais complementam referências LSP, especialmente através de reexports.

## Configuração e verificação

- `.serena/project.yml` seleciona `python` e `typescript` e respeita `.gitignore`. `[tool.pyright]` em `pyproject.toml` indica `.venv` e os quatro diretórios `src` do backend. Prepare as dependências do projeto conforme `m0-local-operation.md`.
- Na máquina avaliada em 2026-11-17, `~/.serena/serena_config.yml` aponta `ls_specific_settings.python.ls_path` e `ls_specific_settings.typescript.ls_path` para os executáveis em `~/.local/bin`. Instalações são locais à máquina, fora dos lockfiles da aplicação. Versões observadas: Pyright 1.1.414 e typescript-language-server 6.1.0. Fixar e atualizar ferramentas de desenvolvimento é escolha do ambiente; não alterar dependências do projeto para instalar esses servidores.
- Verifique `which pyright-langserver typescript-language-server`, `pyright --version` e `typescript-language-server --version`. Se ausentes, instale versões explícitas em um prefixo de ferramentas local e configure os caminhos absolutos no arquivo global; confira o Node e reinicie o processo MCP Serena. A instalação exata depende do gerenciador de pacotes do ambiente.
- O cliente gerado usa TypeScript 6.0.3 e a aplicação web 7.0.2; confirme a versão do serviço TypeScript realmente carregada pelo servidor e valide referências após atualizações. A versão do executável language server não comprova qual versão do TypeScript ele carregou.
- Dashboard global: `web_dashboard: true`, `web_dashboard_open_on_launch: false`, endereço local `127.0.0.1`; disponível manualmente na porta informada pelo processo. Evite expor o dashboard na rede.

## Evidência e limitações (2026-11-17)

Na sessão Serena ativa, referências de `DiagnosticCreate` em `backend/core/src/resume_core/contracts.py` encontraram usos na API e nos testes. O hover reconheceu o modelo Pydantic e seu campo. Diagnósticos em `backend/api/src/resume_api/app.py` e `apps/web/src/diagnostic.ts` não retornaram erros; os arquivos `backend/core/src/resume_core/contracts.py` e `backend/api/src/resume_api/routers/career.py` retornaram erros de tipos, respectivamente no argumento de mensagem e no alias `confirmationField`.

A referência de `bootstrapSession` em `packages/api-client/src/generated/sdk.gen.ts` retornou vazia, embora CodeGraph e `rg` encontrem o reexport e o uso em `apps/web/src/diagnostic.ts`. A causa não foi estabelecida. Antes de renomear ou remover símbolos, confira usos com CodeGraph e `rg`; não interprete resposta vazia como ausência de referências.

`pyright` na raiz terminou com 125 erros, incluindo erros em código e testes. Alguns podem refletir inferência estática, aliases ou construções dinâmicas de Pydantic; não foram todos triados e não se deve desativá-los em bloco nem tratar Pyright como gate aprovado. Verifique os diagnósticos no contexto e execute os gates previstos em `AGENTS.md`. A avaliação não modifica o comportamento da aplicação.
