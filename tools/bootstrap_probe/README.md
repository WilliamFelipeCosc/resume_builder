# Prova Linux do bootstrap (T4)

PASS em 2026-11-11 no Nobara Linux 44, Python 3.14.8, Playwright Test 1.65.0 e Chromium headless 158.0.8127.18. Experimento isolado; não é autenticação de produção. A promoção em T13 ainda implementará validação completa de diretórios/owner, lifecycle e lock de instância.

Comandos executados, com permissão para sockets/processos fora do sandbox:

```sh
.venv/bin/pytest tests/smoke tests/integration/test_bootstrap_probe.py -q
PLAYWRIGHT_BROWSERS_PATH=/tmp/resume-builder-playwright node apps/web/node_modules/@playwright/test/cli.js test --config apps/web/playwright.probe.config.ts
```

Resultado: 15 Python passed (5 smoke + 10 probe); 1 navegador passed. Ruff check/format e typecheck TS passaram. Para obter somente binários de teste, sem instalar dependências do sistema: `PLAYWRIGHT_BROWSERS_PATH=/tmp/resume-builder-playwright node apps/web/node_modules/@playwright/test/cli.js install chromium`. O cache em /tmp é descartável; repetir download se limpo.

A prova usa porta loopback temporária e diretório temporário privado 0700/socket 0600; o app manterá origem canônica 127.0.0.1:8000. Verificou SO_PEERCRED real e recusa quando o UID esperado difere do UID do peer. Não houve processo impersonando outro usuário Linux.

Ticket de 256 bits, consumo concorrente único e validade estrita de 30 s foram verificados. Chromium aceitou cookie opaco HttpOnly/SameSite Strict/Path=/, sem Expires/Max-Age, em HTTP loopback. Ticket retirado do fragmento antes de fetch, ausente de URLs HTTP e logs; cookie não acessível a JS, localStorage vazio. Reuso de ticket recebe 401; reload conserva sessão; reiniciar servidor na mesma origem invalida cookie. Logs JSON são allowlisted e não contêm sentinela/ticket/cookie.

Limites: Chromium headless de teste usa build Ubuntu fallback, pois Nobara não é distribuição oficialmente suportada pelo Playwright. Não valida navegador desktop padrão, Firefox, launcher GUI, segurança completa do servidor HTTP stdlib ou o fluxo definitivo FastAPI. Nenhum browser integrado à aplicação foi criado; Playwright é apenas harness externo de teste. Nenhum arquivo profissional/privado é usado.
