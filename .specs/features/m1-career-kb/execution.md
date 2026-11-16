# M1 — Registro de execução

## T1 — baseline

- Início de trabalho ativo: 2026-11-16 20:18:14 -03; autorização explícita do proprietário às 20:17 -03.
- Estado inicial: `main` em `d2a609d`, com `.specs/STATE.md` e `docs/decisions/open-decisions.md` modificados e planejamento M1 não rastreado; preservados. Branch local `feature/m1-career-kb` criada após aprovação de acesso a `.git`.
- Espera: criação da branch aguardou aprovação de sandbox; duração exata não instrumentada.
- Plano: executar BUILD integral existente, registrar contagens e falhas reais, sincronizar estado e rastreabilidade antes do commit documental.

- BUILD inicial no sandbox: falhou antes da coleta (0 testes) por cache uv somente leitura; repetido com permissão.
- BUILD escalado inicial: 435 Python passaram (2 avisos de depreciação), 17 Vitest passaram, typecheck/build/contrato passaram; Playwright 0/1 executado, falhou ao iniciar por headless shell ausente. Instalação autorizada do Chromium v1254 em `/tmp/resume-builder-playwright` terminou com exit 0; sistema não oficialmente suportado, fallback Ubuntu 24.04.
- BUILD repetido: PASS em 2026-11-16 20:24 -03: 435 Python (2 avisos), 17 Vitest, 1 probe e 2 testes de aplicação Playwright passaram; typecheck, build, contrato (duas gerações idênticas), Ruff e `git diff --check` passaram. Comando: `env PATH=/home/williamf/.local/share/pnpm/bin:/home/williamf/.nvm/versions/node/v24.18.0/bin:/home/williamf/.local/bin:/usr/local/bin:/usr/bin:/bin PLAYWRIGHT_BROWSERS_PATH=/tmp/resume-builder-playwright just check`.
- Intervalo ativo e esperas até 20:24:54 -03: início instrumentado 20:18:14; duração líquida e limites individuais de espera não medidos, `unknown`. As esperas por aprovação, instalação e gates não são somadas como trabalho ativo; duração detalhada `unknown`.
- Intervenções: autorização de início às 20:17 e aprovações de sandbox; CI remoto NOT_RUN. Retrabalho: instalação de Chromium e repetição do gate, duração `unknown`. Tokens/custo `unknown`; verificador independente e aceite humano pendentes; nenhuma exceção aceita.
- MONE-38 parcialmente atendido pelo registro e baseline; medição continua até o encerramento. Próximo: T2.
