# M0 — Desenho da foundation

**Status:** Approved pelo proprietário em 2026-11-11, incluindo schema, bootstrap e limite de validade da tentativa de 30 s. Prova técnica do bootstrap ainda obrigatória.
**Spec:** [spec.md](spec.md). **Contexto:** [context.md](context.md).
**Data:** 2026-11-11. Implementação, instalação e testes de aplicação: NOT_RUN.

## Architecture Overview

React/Vite produz a Web estática servida pela FastAPI em `http://127.0.0.1:8000`. A mesma origem serve `/api`, evitando CORS e uma segunda origem de autenticação em M0. Desenvolvimento inicial usa build/watch do Vite; HMR com servidor separado não é requisito. API e Worker compartilham serviços de aplicação e repositório SQLAlchemy; Redis transporta somente IDs e correlação, SQLite é canônico.

A abordagem aprovada usa a própria execução como intenção durável. Um reconciliador no ciclo de vida da API recupera entrega e tentativas abandonadas. Não há outbox separada. Alternativa considerada: outbox com publicador dedicado, mais reutilizável para múltiplos eventos, mas acrescenta tabela e coordenação sem necessidade no diagnóstico. Isso não estabelece padrão obrigatório para eventos futuros.

Uma instância da API por ambiente, com lock de processo; um Worker inicialmente com um processo/uma thread. Escritas SQLite são transações curtas, serializadas pelo banco; nenhuma chamada ao Redis ou processamento ocorre dentro de transação. WAL não permite vários escritores simultâneos. Configuração de busy timeout e retry limitado será testada, sem consumir silenciosamente o prazo total.

## Code Reuse Analysis

Não há runtime API/Web/Worker existente a reutilizar no checkout revisado (`c7d3497`). Reutilizar as fronteiras e composição de pacotes de `docs/architecture/overview.md`, aliases camelCase de `docs/contracts/rest-openapi.md` e ADRs 001/002/003/007/012. Templates em `assets/` não participam do diagnóstico; nenhum arquivo em `private/` é necessário.

## Components

Todos os caminhos abaixo são propostos, ainda inexistentes.

| Componente / localização | Responsabilidade e interface | Dependências / reuso |
|---|---|---|
| `backend/core/` | `DiagnosticService.create(key, principal)`, `latest(principal)`; validar política antes do repositório | Contratos aprovados; domínio independente de FastAPI |
| `backend/core/` — repositório | Inserir intenção, adquirir posse, concluir condicionalmente, reconciliar vencimentos | SQLAlchemy 2/SQLite, transações atômicas |
| `backend/api/` | Rotas Pydantic/OpenAPI, limites, sessão, Host/Origin e erros sanitizados | Serviço autorizado; servir build da Web |
| `backend/api/` — reconciliador | Tick de 1 s, publicação e recuperação com operações condicionais | Mesmo repositório; adapter Redis com timeout |
| `backend/worker/` | Actor recebe ID/requestId, adquire posse, executa fixture e conclui | Serviços compartilhados; Dramatiq/Redis |
| `backend/api/` — launcher | Canal Unix autenticado pelo UID; emissão/resgate de ticket | Biblioteca padrão Python/Linux; sessão em memória |
| `backend/migrations/` | Upgrade/downgrade inicial, execução serializada explícita | Alembic; rollback somente em teste temporário |
| `apps/web/` | Executar, consultar último estado, aviso transitório e erro final | React/Vite; cliente gerado; Vitest |
| `packages/api-client/` | Tipos e chamadas gerados a partir do OpenAPI | Sem DTO manual; gerador a selecionar por nota técnica |

`backend/core`, `backend/api` e `backend/worker` serão membros uv; frontend e cliente serão membros pnpm. Justfile expõe instalação de dependências do projeto, migração, build, API, Worker, abertura e checks. Redis inicia manualmente. Nada inicia provider ou MCP.

## Data Models

### Proposta de schema — depende da revisão deste desenho

Uma tabela `diagnostic_runs`, sem domínio profissional:

- Campos públicos aprovados de `spec.md`, com `deliveryWarning` nullable; nomes físicos snake_case e aliases Pydantic camelCase.
- `id` chave primária; `idempotency_key` unique; UUIDs validados em runtime.
- `status` com CHECK dos cinco estados; `attempt_count` CHECK entre 0 e 3.
- `created_at` e `updated_at` em UTC; persistência em representação única normalizada. Comparações de prazo usam o mesmo relógio de aplicação injetável, nunca strings com offsets diferentes.
- `result` contém exclusivamente o objeto fixo aprovado; `error` e `delivery_warning` contêm códigos de allowlist e mensagens constantes. Nenhum texto livre de exceção.
- Campos internos propostos: `lease_token`, `lease_expires_at`, `next_delivery_at`. Posse é identificador aleatório interno, nunca retornado pela API. Prazo total deriva de `created_at + 120 s`.
- Índice unique parcial sobre uma constante para estados ativos garante uma única execução ativa no banco, inclusive com POSTs concorrentes. Unicidade não depende apenas do botão.
- CHECKs de consistência: sucesso exige resultado e ausência de erro/aviso; falha exige erro e ausência de resultado/aviso; estados ativos não têm resultado/erro final.

Não há tabela de sessão, dados privados ou outbox. Migração cria/remove somente esses objetos. Dados por ambiente em `$XDG_DATA_HOME/resume-builder/<ambiente>/`; testes exigem caminhos temporários explícitos. Migração nunca roda implicitamente em requests.

## Entrega, posse e recuperação

1. POST autorizado valida o corpo e reconcilia vencimentos. Em transação, procura chave existente antes de verificar conflito ativo: mesma chave retorna a mesma execução; chave distinta com ativa retorna 409; caso contrário cria `pending` e commita antes da publicação.
2. Reconciliador tenta publicar quando `next_delivery_at` vencer. Payload da fila contém somente ID e requestId canônicos. Falha de Redis mantém a intenção e grava `deliveryWarning={code: queue_unavailable, message: ...}`. Nova tentativa de entrega no próximo tick; timeout de conexão/publicação menor que o intervalo, sem bloquear o event loop.
3. Publicação reconhecida muda `pending` para `queued` condicionalmente e limpa aviso. Worker pode consumir antes dessa escrita: atualização do publicador não regride `running` ou estado terminal. Sucesso no Redis seguido de crash antes do commit pode gerar mensagem duplicada; isso é esperado.
4. Para também recuperar perda da fila após confirmação, estados `pending/queued` sem posse recebem reentrega limitada a uma por segundo até claim/prazo. `next_delivery_at` controla frequência; envio externo nunca fica dentro da transação.
5. Worker adquire posse por UPDATE condicional atômico: estado `pending/queued`, tempo menor que prazo e tentativas <3. Incrementa contador e muda para `running` na mesma transação; lease vence em `min(início + 30 s, prazo total)`. Duplicata sem claim não inicia processamento nem incrementa contador.
6. Fixture pura retorna `{message: diagnostic_completed, fixtureVersion: m0-v1}`. Não faz efeitos externos. Commit de sucesso exige token atual, `running`, posse não vencida e prazo total não vencido. Ao atingir exatamente o limite, conclusão é rejeitada.
7. Falha da tentativa libera a posse; se ainda há orçamento, volta a `pending`. Posse abandonada é recuperada pelo reconciliador ao vencer. Na terceira falha ou no prazo total, muda para `failed`, limpando posse e aviso. Estados terminais nunca retornam ao processamento.
8. Tick reconcilia expiração antes de entregar. Startup reconcilia antes de servir diagnósticos; a leitura também impede apresentar estado ativo vencido. API desligada não atualiza estado; Worker ainda verifica prazos no claim/commit.

Códigos finais propostos: `deadline_exceeded`, `attempts_exhausted`; falhas internas inesperadas usam código sanitizado. Todas as mensagens são constantes. `updatedAt` muda somente ao alterar o registro, nunca por polling puro.

O prazo de 30 s é de validade da tentativa: nenhuma tentativa pode produzir efeito válido depois dele. Dramatiq TimeLimit é proteção adicional, não garantia de interrupção de syscall. A fixture é limitada e cooperativa; operações de banco/broker têm timeouts próprios. Um teste de interrupção deve comprovar rejeição de um Worker antigo após nova posse. O proprietário aprovou esta semântica de validade em 2026-11-11. Não alegar encerramento físico de código bloqueado aos 30 s.

Retries do diagnóstico pertencem ao serviço/reconciliador, não ao contador automático do broker. Configurar o actor para não criar retries automáticos concorrentes; redelivery do broker ainda deve ser segura. Controlar/sanitizar logs de middleware, além dos logs próprios.

## Abertura local e sessão — proposta com prova técnica obrigatória

- API escuta apenas `127.0.0.1:8000`, sem proxy externo nem confiança em forwarded headers. Host exato; Origin presente deve coincidir exatamente com a origem canônica. Nenhuma permissão CORS ampla.
- API abre socket Unix em diretório privado 0700 sob XDG_RUNTIME_DIR; socket 0600. Verificar owner/tipo do diretório, recusar symlinks e conflitos de instância. Não remover socket pertencente a processo vivo.
- Comando local pede ticket pelo socket. Servidor verifica UID do peer Linux (`SO_PEERCRED`) contra seu UID; permissões do path são defesa adicional. Falta de runtime dir seguro é erro explícito, sem fallback público.
- Ticket aleatório de 256 bits, em memória, uso único, TTL de 30 s; CLI abre `/#bootstrap=<ticket>` no navegador padrão. Fragmento não é enviado no request HTTP; não imprimir URL/ticket. Página limpa fragmento com history.replaceState antes de chamadas externas e envia ticket por POST same-origin em corpo limitado.
- `POST /api/session/bootstrap` valida Origin exato, tipo JSON, limite e ticket; consome ticket atomicamente e devolve cookie aleatório opaco `HttpOnly; SameSite=Strict; Path=/`, sem Domain, Expires ou Max-Age. Em HTTP loopback não presumir disponibilidade de cookie Secure; validar comportamento no navegador alvo. Cookie aceito apenas se constar no armazenamento em memória da instância API.
- Token de sessão não vai a localStorage. Reinício apaga sessões/tickets; cookie antigo recebe 401. Nova abertura pode criar outra sessão válida. Endpoint bootstrap é a única troca sem sessão, autorizada pelo ticket; não lê dados de diagnóstico.
- Escritas de diagnóstico exigem sessão + Origin exato + JSON; ausência de Origin em escrita recebe 403. Leituras sem Origin requerem sessão; Origin estranho é rejeitado também em leitura. Header X-Request-ID do cliente não é confiável: gerar UUID no servidor.
- Health público retorna apenas liveness. Web sem sessão mostra instrução de abertura; docs/OpenAPI por HTTP exigem sessão (export offline para geração). Cache-Control no-store para sessão e diagnóstico; Referrer-Policy no-referrer e CSP sem scripts externos na página de bootstrap.
- Logs HTTP não registram URL de lançamento, corpo, cookies, headers de credencial ou exceção crua. Usar eventos e campos permitidos; mascaramento por regex isolado não é política suficiente.

Modelo de ameaça: protege acesso de outros UIDs e origens web, não processos comprometidos do mesmo usuário Linux. Não há segredo permanente; não substituir keyring por arquivo persistente. Nenhum controle do navegador: o launcher somente abre URL no navegador padrão do usuário.

A prova técnica, antes da implementação da autenticação, deve validar UID, ticket de uso único/expirado, cookie no navegador, limpeza do fragmento, reinício e ausência de vazamento em logs. Usar dados sintéticos e teste isolado; se falhar, revisar com o proprietário. Nenhum destes resultados foi obtido ainda.

## HTTP e comportamento da Web

| Operação / situação | Resposta proposta |
|---|---|
| GET health | 200, liveness mínimo |
| POST diagnostics — nova intenção | 202, execução persistida |
| POST diagnostics — mesma chave | 200, mesma execução, inclusive terminal |
| GET diagnostics/latest | 200, envelope `execution` nullable; vazio não é erro |
| Sem sessão / Host ou Origin recusado | 401 / 403, antes de consultar diagnósticos |
| Intenção distinta enquanto ativa | 409, sem nova linha |
| Corpo maior que 1024 bytes / contrato inválido | 413 / 422; leitura limitada mesmo sem Content-Length |

Erros de validação não ecoam input Pydantic cru. Ordem: Host/Origin, sessão (exceto health/bootstrap), limite de corpo, contrato, serviço. Identificador canônico da criação permanece em `execution.requestId`; cada resposta/log também tem seu próprio requestId de transporte.

Web gera idempotencyKey uma vez por clique intencional e reutiliza em retry de transporte. Desabilita botão durante POST e estado ativo. Erro de rede não implica falha do job: consulta latest e preserva chave até resolver a intenção. Polling de 1 s sem requests sobrepostos; 401 interrompe polling e orienta abertura local; demais falhas mostram indisponibilidade sem inventar estado terminal. Reabertura mostra última execução, sem histórico. `deliveryWarning` aparece junto de pending; sucesso/erro final mostra o conteúdo persistido aprovado.

## Verification Strategy

Testes derivam dos FNDs, com relógio injetável e fixtures exclusivamente sintéticas.

| Cobertura | Evidência exigida |
|---|---|
| FND-01/02/05/06/12 | SQLite real: intenção antes do envio, mesma chave, POSTs concorrentes, efeito único, conclusão tardia recusada |
| FND-07/08 | Redis real desligado/religado; aviso visível, mesmo ID retomado, aviso removido |
| FND-09/10/11 | Worker real interrompido durante tentativa controlada, retomada; relógio cobre 30/120 s e terceira tentativa, token antigo rejeitado |
| FND-03/04 | Vitest para botão/polling/reabertura; demonstração Web→API→Worker real |
| FND-13…18 | Bootstrap/UID/sessão/restart, Host/Origin/CSRF, corpo chunked acima do limite, campos extras, sentinelas ausentes em logs/erros |
| FND-19/20 | Alembic upgrade/downgrade/upgrade em SQLite temporário; OpenAPI exportado, geração reproduzível e typecheck |
| FND-21…23 | Comandos locais documentados e versões capturadas; ambientes isolados; Redis manual; nenhum acesso a private |

Controle de interrupção/demora existe apenas no harness de teste, não como endpoint público ou opção de payload. UI pode ser verificada por Playwright Test externo como teste do app; não é feature de controle de navegador/candidaturas. Verifier independente após implementação, com evidência por AC e discriminação em cópia isolada. Nenhum teste executado nesta fase.

## Risks & Concerns

| Risco / fonte | Impacto | Mitigação |
|---|---|---|
| FND-10: timeout de thread não mata syscall | Garantia exagerada de 30 s | Posse/prazo no commit, fixture limitada, timeouts de I/O; revisar isolamento se exigido |
| FND-07 vs error terminal | Aviso transitório impossível de representar | deliveryWarning aprovado separado e limpo ao recuperar |
| FND-08/09: falha entre broker e banco | Duplicatas ou mensagem perdida | Reentrega limitada, claim e conclusão condicionais |
| FND-13: bootstrap ainda sem prova | Abertura não funcionar no Linux/navegador alvo | Prova isolada antes de autenticação definitiva |
| ADR-003: contenção SQLite | Falhas ou latência de escrita | Transações curtas, busy timeout limitado, testes concorrentes |
| Contrato gerado e versões ainda sem locks | Incompatibilidade Python/Node/gerador | Seleção e nota técnica antes de instalar; lockfiles e geração determinística |
| Ausência de runtime/testes existentes | Desenho sem validação operacional | Não declarar M0 concluído; gates unitários, integração real e Web |

## Tech Decisions e pesquisa

- Registro durável + reconciliador e deliveryWarning aprovados pelo proprietário em 2026-11-11. Detalhes deste arquivo aprovados em 2026-11-11; não reabrem ADRs.
- Origem única com build Vite serve a mesma funcionalidade com menor superfície de CORS. Bootstrap Unix é específico ao M0 Linux; não define auth MCP ou Tauri.
- Não adicionar bibliotecas de UI, scheduler, autenticação ou outbox nesta fase. Versões de Python/Node e dependências, gerador TS e topologia Redis serão fixados em nota técnica na execução após verificar compatibilidade, sem instalar ferramentas do sistema automaticamente.
- Pesquisa Context7 `/bogdanp/dramatiq` e [guia oficial Dramatiq](https://dramatiq.io/guide.html): redelivery exige idempotência; TimeLimit é best effort e não cancela syscalls.
- [Python socket](https://docs.python.org/3/library/socket.html): sockets Unix e capacidades específicas de plataforma; SO_PEERCRED depende de prova no Linux alvo.
- [MDN Set-Cookie](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie): HttpOnly, SameSite e atributos do cookie; suporte concreto em loopback será testado.

## Próximo gate

Desenho aprovado, incluindo schema e semântica do limite de tentativa. Próximo gate: aprovar tasks.md validado antes de executar. Não há tasks.md vazio nem runtime antecipado.
