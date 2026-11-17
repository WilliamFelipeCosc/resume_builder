# Índice da documentação

- `roadmap/`: milestones M0–M7 e critérios de aceite.
- `architecture/`: visão geral, modelo de dados, segurança, operação local e ADRs.
- `modules/`: comportamento de cada subsistema da V1.
- `contracts/`: estruturas conceituais de API, eventos, MCP e revisões.
- `decisions/`: decisões ainda abertas, não tomar como aprovação.
- `references.md`: fontes técnicas oficiais a verificar antes de codificar.
- [specification-sync-2026-11-11.md](specification-sync-2026-11-11.md): importação pública, decisões do kickoff e limites de execução.
- [requirements.md](product/requirements.md): IDs REQ preservados e reconciliados com o pacote atual.
- `history/`: proveniência histórica; não usar como especificação ativa.

## Autoridade e estado

Conforme [ADR-013](architecture/adr/ADR-013.md), os requisitos aprovados ficam em `product/`, `modules/`, `contracts/`, `roadmap/` e nas specs aprovadas de features em `../.specs/features/`. Os ADRs registram decisões arquiteturais. Aprovação posterior registrada prevalece dentro de seu escopo; divergências entre fontes aprovadas devem ser reportadas e reconciliadas. Propostas/OPEN, exemplos conceituais e detalhes de implementação não alteram requisitos por si.

[PROJECT_OVERVIEW.md](../PROJECT_OVERVIEW.md) é o resumo de entrada. Os documentos completos originais foram arquivados externamente; a [migração e seu mapa de preservação](process/documentation-migration-2026-11-17.md) registram a transição, sem redução de V1/V2. Registros de importação e `history/` são fontes históricas, não instruções ativas.

- **Estado de marcos:** [milestone-status.json](process/milestone-status.json).
- **Planos e retomada:** [STATE.md](../.specs/STATE.md) e spec/design/tasks da feature.
- **Evidências:** execution/validation da feature; testes verdes não equivalem a aceite humano.
- **Obsidian:** projeção sincronizada conforme [workflow](process/milestone-status-workflow.md); não substitui fontes canônicas.

Contagens, branches e ambiente são snapshots datados, não regras permanentes. O ambiente e as permissões atuais vêm da sessão efetiva.
