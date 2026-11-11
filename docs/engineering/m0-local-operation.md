# M0 — operação e evidências locais

M0 entrega um diagnóstico sintético Web → FastAPI → SQLite → Redis/Dramatiq → Worker → Web. As tarefas T1–T22 têm evidências em [tasks.md](../../.specs/features/m0-foundation/tasks.md); a [validação independente](../../.specs/features/m0-foundation/validation.md) passou para os 23 FNDs e AC-M0-001/002, com 254 Pytest, 17 Vitest, 3 Chromium e oito mutações detectadas. Isso não entrega currículo, providers, MCP ou M0.5.

## Preparar

Ferramentas previamente instaladas pelo operador: Linux com Python 3.14, uv, Node 24.18, pnpm 11.28.9, just, Docker/Compose e xdg-open. Veja as versões verificadas e a correção de compatibilidade do gerador em [m0-toolchain.md](m0-toolchain.md). Os comandos não instalam ferramentas do sistema.

```sh
just setup
just build
```

`setup` instala apenas dependências do projeto com `uv.lock` e `pnpm-lock.yaml`. Para os testes de navegador, instalar Chromium explicitamente como dependência de teste, sem instalar pacotes do sistema:

```sh
export PLAYWRIGHT_BROWSERS_PATH=/tmp/resume-builder-playwright
pnpm --filter web exec playwright install chromium
```

O cache temporário poderá precisar ser recriado depois de reiniciar o Linux. Dependências de sistema ausentes geram falha explícita; não executar instalação automática de bibliotecas do sistema.

## Operar

Executar cada serviço em seu terminal, a partir da raiz do repositório:

```sh
just redis-up
just migrate
just api
```

Em outro terminal:

```sh
just worker
```

Abrir a Web pelo comando local:

```sh
just open
```

A API serve o build Vite e REST em `http://127.0.0.1:8000`, sem proxy ou CORS amplo. O comando solicita um ticket ao socket Unix privado e chama o navegador padrão via xdg-open; não imprime ticket/URL e descarta stdout/stderr do navegador. O fragmento é limpo antes do resgate HTTP. URL direta sem cookie mostra a instrução de abertura. Cookie HttpOnly/SameSite Strict vive só na memória da instância; reiniciar a API exige nova abertura local. `/docs` e `/openapi.json` exigem sessão; `/api/health` retorna apenas `{"status":"ok"}`.

`XDG_RUNTIME_DIR` deve existir, pertencer ao UID atual e ter modo privado, como `/run/user/<uid>` da sessão Linux. Ausência, symlinks, permissões inseguras ou outra API no mesmo ambiente causam falha; não há fallback público. O launcher de desktop foi testado com opener injetado; a integração real foi validada em Chromium headless, sem alegar abertura do navegador padrão do desktop nesta sessão.

Redis inicia apenas em `just redis-up`. Compose usa imagem fixada por digest, porta `127.0.0.1:6379`, tmpfs e sem persistência. API/Worker não executam Docker nem iniciam Redis. Se a porta estiver ocupada, corrigir a configuração do operador; não há fallback silencioso. Reiniciar o broker pode perder mensagens: o registro SQLite é a intenção durável e o reconciliador a reentrega.

Parar API/Worker com Ctrl-C antes de migrar ou limpar dados. Encerrar o Redis explicitamente:

```sh
just redis-down
```

## Dados, limites e limpeza

No ambiente development, o banco fica em `${XDG_DATA_HOME:-$HOME/.local/share}/resume-builder/development/diagnostics.sqlite3`. Config/cache/state seguem seus respectivos diretórios XDG, com subdiretório de ambiente. Migração é comando explícito, serializado por lock; nunca ocorre durante requests ou startup do servidor. `serve` recusa banco ausente. Logs JSON sanitizados vão a stderr, sem arquivo de log por padrão.

Nenhum comando operacional lê `private/` ou seeds pessoais. Testes exigem `--environment test --test-root /tmp/<diretório-dedicado>` e usam SQLite temporário, namespaces Redis únicos e somente dados sintéticos. CLI avançada, usada pelo harness:

```sh
uv run --all-packages --locked python -m resume_api --environment test --test-root /tmp/rb-example migrate
```

Não executar o exemplo sobre diretório de dados pessoal. Limpeza de dados persistidos é manual: pare os serviços, confira o ambiente e o caminho e remova somente a pasta sintética escolhida se não precisar mais dos registros. Não há comando automático que apague dados de desenvolvimento; não apagar apenas o arquivo SQLite enquanto há processos ou arquivos WAL/SHM em uso.

Uma execução ativa por ambiente, mesma chave retorna o mesmo ID. Prazo total 120s; até três inícios efetivos; posse válida por até 30s. Exatamente no limite, o efeito é recusado. Isso não promete matar fisicamente código bloqueado aos 30s. Aviso transitório de entrega é separado de falha terminal; novo clique após terminal cria outra intenção. A UI restaura somente a última execução e faz polling de 1s sem sobreposição.

## Verificar

Com Docker disponível e Chromium instalado no cache escolhido:

```sh
export PLAYWRIGHT_BROWSERS_PATH=/tmp/resume-builder-playwright
just check
```

O check executa Pytest (unit/integration/smoke), Vitest, TypeScript, build, duas gerações de contrato em diretórios temporários, Chromium probe e Chromium da aplicação definitiva, Ruff/format e whitespace. Os testes Redis iniciam e encerram somente seus containers descartáveis, em portas efêmeras de loopback; não usam o serviço de desenvolvimento. Nenhum teste envia candidatura real, inicia provider ou usa dado profissional.

`check-python` usa `/tmp/rb-tests` como basetemp curto: sockets AF_UNIX têm limite de 108 bytes. O Pytest limpa somente essa raiz de testes. Para executar seleção focal, por exemplo:

```sh
uv run --all-packages --locked pytest tests/integration/test_real_recovery.py -q --basetemp=/tmp/rb-recovery
```

`just check-contract` compara schema e SDK sem reescrever os arquivos reais. Mudanças intencionais de Pydantic exigem `just generate`, revisão do diff e novo check. O frontend usa DTOs e chamadas gerados; o gerador tem TypeScript 6.0.3 local por incompatibilidade comprovada com a API de compilador do TS7; o frontend conserva TS7.

## Evidência desta execução

T22 verificou comandos CLI reais no harness definitivo: migrate explícito, API e Worker em processos separados, Redis real, build estático, ticket Unix e cookie no Chromium, diagnóstico persistido, reabertura e reinício real da API invalidando o cookie anterior e preservando o resultado no banco. Teste manual posterior: Abertura autorizada no navegador desktop e diagnóstico concluído com sucesso confirmados pelo proprietário em 2026-11-11 às 16:53 (America/Sao_Paulo).

Os seis cenários de T21 cobrem Redis offline/online, perda da fila confirmada, Worker morto/reiniciado após claim, Worker antigo que tenta concluir após nova posse, prazo total e terceira falha. O relógio controlado e os sinais ficam exclusivamente no harness externo de testes. API e payload públicos não têm comandos de fault injection.

Warnings observados: depreciação Starlette TestClient/HTTPX e configuração NO_COLOR/FORCE_COLOR do runner. O pnpm embarcado no sandbox pode reportar Node26 enquanto os scripts rodam com Node24.18; instalação frozen e ambiente autorizado foram verificados. Não foram adicionadas dependências para silenciar warnings. Contagens finais e comandos efetivamente executados são registrados em tasks.md; validação independente em validation.md após o fechamento do lote.
