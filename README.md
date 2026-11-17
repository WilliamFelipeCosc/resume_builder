# Resume Builder

Aplicação local-first para Career Knowledge Base, currículos fundamentados em evidências e contexto autorizado para agentes CLI externos. A primeira entrega utilizável prioritária é M3; o escopo completo de V1 permanece no roadmap.

## Onde começar

1. [Visão geral e proveniência](PROJECT_OVERVIEW.md).
2. [Instruções para agentes](AGENTS.md) e guias locais aplicáveis.
3. [Índice e autoridade documental](docs/README.md), [requisitos](docs/product/requirements.md), [roadmap](docs/roadmap/milestones.md) e [aceite](docs/roadmap/acceptance-criteria.md).
4. [Arquitetura](docs/architecture/overview.md), [ADRs](docs/architecture/adr/), [módulos](docs/modules/) e [contratos](docs/contracts/).
5. [Estado canônico dos marcos](docs/process/milestone-status.json) e [ponte para execução/evidências](.specs/STATE.md).

Requisitos planejados não significam implementação ou aceite. As notas do Obsidian são resumos sincronizados com as fontes do repositório.

## Executar e verificar

Siga [operação local](docs/engineering/m0-local-operation.md) e `just --list`. Dependências e serviços externos têm instalação/inicialização explícita. O gate integral é `just check`; os comandos por área estão em [AGENTS.md](AGENTS.md).

`MANIFEST.sha256` registra hashes da árvore pública versionada no momento de sua atualização, excluindo o próprio manifesto; confira com `sha256sum --check MANIFEST.sha256`. Não comprova testes nem ausência de alterações posteriores. Manifestos históricos permanecem em [docs/history/](docs/history/).

## Privacidade e referências

Currículos pessoais e seeds não entram no Git, CI, logs ou vault por padrão. `private/` é ignorado; importações permanecem sujeitas à revisão humana. Os templates em [assets/resume-templates/](assets/resume-templates/) preservam estilo sem publicar os dados pessoais. O gerador de referência não é o renderer definitivo.

Os documentos completos de referência foram arquivados externamente, conforme a [migração documental](docs/process/documentation-migration-2026-11-17.md). O projeto pode ser compreendido e desenvolvido com a documentação modular versionada.
