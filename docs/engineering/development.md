# Desenvolvimento e convenções

## Monorepo

Usar pnpm Workspaces para React/TypeScript, uv workspaces para Python e justfile para comandos comuns (DECIDED). Comandos, versões, lockfiles e geração do cliente TypeScript foram implementados em M0. Consulte [operação e evidências locais](m0-local-operation.md), `just --list` e `just check`. Redis via Compose é iniciado manualmente. Referências: [operação local](../architecture/local-operations.md) e [contrato REST/OpenAPI](../contracts/rest-openapi.md).

**Ambiente verificado em 2026-11-11:** pnpm instalado pelo proprietário e disponível no PATH; `pnpm --version` retorna `11.28.9`. A seleção/pin da versão do projeto e a geração do lockfile continuam previstas para M0; nenhuma dependência do projeto foi instalada nesta atualização documental.

## Vertical Slice

Cada incremento entrega uma rota/serviço, UI mínima, persistência e teste de aceitação para um caso de uso. Não construir infraestrutura especulativa do M7 antes de atingir M3. Invariantes mínimos de privacidade/teste entram no M0 e evoluem a cada marco.

## Convenções de versão

Schemas de API/MCP/Dados importados versionados; migrations idempotentes/revisadas; ChangeSets exigem `baseRevisionId`; eventos exigem `idempotencyKey`; adapters de providers e fontes com contratos tipados. APIs externas são dados não confiáveis; validar em runtime.

## Documentação

Mudanças arquiteturais requerem ADR; requisitos mudam apenas com decisão explícita; fonte modular e `PROJECT_SOURCE.md` devem ser sincronizadas. Não presumir que CLAUDE.md ou AGENTS.md são autocarregados em todo harness — configurar clientes individualmente.

## Integração contínua

Decisão do proprietário em 2026-11-11: M0 exige checks reproduzíveis locais; GitHub Actions será introduzido em M1, antes do domínio profissional. Não criar workflow em M0. Isso não elimina os Quality Gates ou a exigência de CI na evolução da V1.

Testes determinísticos em PR/CI, sem cobrança automática de API nem acesso a contas de recrutamento. AI live eval controlado, com base sintética/consentida e orçamento fixado. Checklist de produção por marco; telemetria cloud opt-in.
