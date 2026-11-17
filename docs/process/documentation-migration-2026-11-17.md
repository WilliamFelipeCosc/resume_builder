# Migração documental — 2026-11-17

O proprietário aprovou a revisão das instruções, guias locais, refinamento das preferências globais e substituição dos dois documentos completos de origem por um overview breve. Esta mudança é documental; preserva o escopo aprovado de V1/V2 e os estados dos marcos, sem executar tarefas M1 ou aceitar marcos.

## Preservação dos originais

Antes de remover os arquivos da árvore, foram copiadas e verificadas byte a byte as versões de trabalho, incluindo alterações não commitadas. Arquivo local externo: `~/Documents/resume-builder-reference/2026-11-17/`, com `archive-sha256.json`. A configuração global anterior foi preservada como `GLOBAL_AGENTS.before.md` no mesmo diretório. Esse caminho não é dependência do clone, build ou CI.

| Original | SHA-256 da cópia preservada |
|---|---|
| `PROJECT_SOURCE.md` | `24b282ecd905a0b860c83f9b20cfd72eed3b4452e82cfcdb71ebdc4172f4cbed` |
| `ARQUIVOS_E_PROVENIENCIA.md` | `53c2608b388c3c6d6d39c1c3ac03f6d5e890321a007760b8146ae81ad947fd66` |

Os nomes antigos são ignorados na raiz para impedir reintrodução acidental. O histórico Git não foi reescrito. Hashes e registros históricos de importação continuam descrevendo seus snapshots originais; não devem ser recalculados para fingir equivalência com a árvore atual.

## Mapa de preservação de requisitos e contexto

A conferência documental relacionou as seções da especificação consolidada às fontes existentes abaixo. Detalhes específicos são mantidos nos módulos/contratos, não copiados integralmente para o resumo.

| Conteúdo de origem | Fontes versionadas preservadas |
|---|---|
| §1 objetivos, M3 prioritário e V1/V2 | [visão](../product/vision.md), [escopo](../product/scope.md), [requisitos](../product/requirements.md), [roadmap](../roadmap/milestones.md) |
| §2 decisões 001–016 | [ADRs](../architecture/adr/); ADR-013 registra esta revisão |
| §3 arquitetura e limites entre componentes | [overview arquitetural](../architecture/overview.md), [modelo](../architecture/data-model.md) |
| §4.1 KB, seed, revisão, contagens e ambiguidades | [Career KB](../modules/career-kb.md), [contrato KB](../contracts/career-kb.md), [spec M1](../../.specs/features/m1-career-kb/spec.md) |
| §4.2 currículo, templates, PDF e ChangeSets | [Resume Studio](../modules/resume-studio.md), [ResumeDocument](../contracts/resume-document.md), [ChangeSet](../contracts/change-set.md), [assets](../../assets/resume-templates/) |
| §4.3 vagas e matching | [Job Intelligence](../modules/job-intelligence.md), [contrato](../contracts/job-intelligence.md) |
| §4.4 respostas | [Application Answers](../modules/application-answers.md) |
| §4.5 MCP/CLIs e §4.6 tracking | [MCP](../modules/mcp-server.md), [tools](../contracts/mcp-tools.md), [context/report](../contracts/application-context.md), [tracking](../modules/application-tracking.md), [spike aprovado](../../.specs/features/m05-mcp-feasibility/spec.md) |
| §4.7 recuperação e providers | [retrieval](../modules/context-retrieval.md), [providers](../modules/ai-providers.md) |
| §5 segurança/consentimento | [segurança](../architecture/security-and-privacy.md) |
| §6 infraestrutura, XDG, backups e Linux | [desenvolvimento](../engineering/development.md), [operação](../engineering/m0-local-operation.md), [backup](../engineering/data-backup.md), [distribuição](../engineering/linux-distribution.md) |
| §7 testes, observabilidade e métricas | [testes](../engineering/testing.md), [observabilidade](../engineering/observability.md), [aceite](../roadmap/acceptance-criteria.md) |
| §8 marcos e §9 V2 | [roadmap](../roadmap/milestones.md), [escopo](../product/scope.md), [estado](milestone-status.json) |
| §10 exemplos conceituais | [contratos](../contracts/README.md), [modelos ilustrativos](../contracts/examples/models.py); não são schemas executáveis novos |
| §11 riscos e §12 escolhas abertas | [riscos](../roadmap/risk-register.md), [OPEN](../decisions/open-decisions.md) |
| §13 navegação e regra de interpretação | [índice](../README.md), [ADR-013](../architecture/adr/ADR-013.md), [overview](../../PROJECT_OVERVIEW.md) |
| Snapshot de implementação acrescentado em 17/11 | [estado de marcos](milestone-status.json), [STATE](../../.specs/STATE.md), [execução M1](../../.specs/features/m1-career-kb/execution.md), [handoff](../../.specs/features/m1-career-kb/handoff.md) |
| Auditoria/proveniência do pacote | [overview](../../PROJECT_OVERVIEW.md), [histórico](../history/), [importação de 11/11](../specification-sync-2026-11-11.md), [inventário original](../package-import-2026-11-11.json) |

As afirmações antigas de que código, lockfiles e SDK não existiam são contexto do pacote inicial; a documentação operacional aponta agora para arquivos e evidências atuais. Não são requisitos a preservar como estado presente.

## Instruções e verificações

A raiz orienta a leitura e mantém invariantes. Guias locais cobrem backend, MCP, web, SDK gerado, testes, documentação e execução. Core/API permanecem sob o guia backend até haver necessidade de especialização adicional. As preferências globais reutilizam aprovações e exigem investigação de contratos existentes antes de perguntas sobre lacunas.

O manifesto da árvore atual cobre arquivos públicos versionados e os novos documentos deste incremento, excluindo o próprio manifesto; os manifestos históricos não são alterados. Evidências dos checks documentais e da sincronização com Obsidian são registradas no fechamento desta migração.

## Evidências da migração

- Arquivos completos preservados com os hashes acima; originais ausentes da árvore, removidos do índice Git e ignorados na raiz. O backup global também foi verificado antes de alterar as quatro preferências de interação; o restante do guia global foi preservado.
- Check documental temporário `python3 /tmp/resume-builder-doc-check-20261117.py`: PASS, 132 destinos de links locais válidos em 46 Markdown alterados/novos; sete cadeias estáticas de instruções conferidas, incluindo backend→MCP; todas abaixo de 32 KiB somadas ao guia global. Esta é uma verificação estrutural, sem iniciar novas sessões de clientes para comprovar carregamento em runtime.
- Cinco registros históricos (diretório `docs/history/`, inventário de importação e sincronização original) conferidos byte a byte contra HEAD, sem alterações.
- Obsidian atualizado pelo MCP com `ifMatch`, preservando histórico narrativo: projeto principal, Planning Summary, Specification Refresh, roadmap principal, índice e M1. Os seis corpos foram relidos e comparados ao conteúdo pretendido; metadados pertinentes também foram atualizados. M1 foi reconciliado de `planned` para o `in_progress` já canônico no repositório, sem alterar o estado canônico ou aceitar o marco.
- [Snapshot recolhido do Obsidian](obsidian-status-2026-11-17.json) contém índice e união dos oito arquivos M0–M7 (M0 inclui M0.5), sem IDs duplicados. `python3 tools/check_milestone_drift.py docs/process/obsidian-status-2026-11-17.json`: exit 0, sem divergência no snapshot fornecido. A hora UTC está no JSON; o snapshot não atesta o estado futuro do vault.
- Verificações finais: `git diff --check`, `git diff --cached --check` e `sha256sum --check --quiet MANIFEST.sha256`: PASS, exit 0. O manifesto atualizado cobre 334 arquivos públicos da árvore versionada e os novos documentos deste incremento; não constitui evidência de testes da aplicação.
- Nenhum teste de runtime, carga privada, provider, candidatura real ou CI remoto executado nesta migração documental. REQs/ACs de produto e gates pendentes do M1 permanecem inalterados.
