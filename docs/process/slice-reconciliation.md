# Reconciliação das slices com os critérios atuais

Fonte de requisitos: `docs/roadmap/acceptance-criteria.md` e `docs/roadmap/milestones.md`. A lista de slices vem das notas M0–M7 em `10 Projects/Personal/Resume Builder/Vertical Slices` no Obsidian. Uma célula parcial não encerra o critério. Os vínculos abaixo são um mapa de planejamento, não evidência de execução.

| Slice | Critérios atuais | Estado / observação |
| --- | --- | --- |
| VS-M0-01 | AC-M0-001 | Aceito; ver `.specs/features/m0-foundation/validation.md`. |
| VS-M0-02 | AC-M0-002 | Aceito; ver mesma validação. |
| VS-M05-01 | AC-M05-001 | Aceito; ver validação M0.5. |
| VS-M05-02 | AC-M05-001, AC-M05-002 | Aceito; exceção histórica SPIKE-17 em `.specs/features/m05-mcp-feasibility/historical-exception.md`. |
| VS-M1-01 | AC-M1-001 parcial | Planejado. |
| VS-M1-02 | AC-M1-001 parcial | Planejado. |
| VS-M1-03 | AC-M1-001 parcial, AC-M1-002/003 | Planejado; a nota antiga omite importação privada, staging `pending_review`, deduplicação e revisão/aprovação. O detalhamento de M1 deve cobrir os três ACs integralmente; esta associação não altera o escopo aprovado. |
| VS-M2-01 | AC-M2-001 parcial, AC-M2-002 | Planejado; a nota antiga omite o template visual padrão e a alternativa ATS. |
| VS-M2-02 | AC-M2-001, AC-M2-003 | Planejado; PDF de ambos os templates, extração e paginação são exigidos. |
| VS-M3-01 | AC-M3-001, AC-M3-003 parciais | Planejado. |
| VS-M3-02 | AC-M3-001, AC-M3-002 parciais | Planejado. |
| VS-M3-03 | AC-M3-001, AC-M3-002 parciais | Planejado; não implica que vision está disponível. |
| VS-M3-04 | AC-M3-003, AC-M3-006 parciais | Planejado. |
| VS-M3-05 | AC-M3-004, AC-M3-006 parciais | Planejado. |
| VS-M3-06 | AC-M3-001–006 | Planejado; consolidação dos seis critérios, incluindo os três modos de entrada. |
| VS-M4-01 | AC-M4-001 parcial | Planejado. |
| VS-M4-02 | AC-M4-002 parcial | Planejado. |
| VS-M4-03 | AC-M4-001/002 | Planejado; validar HTTP e clientes reais no escopo definido. |
| VS-M5-01 | AC-M5-001 parcial | Planejado. |
| VS-M5-02 | AC-M5-001 | Planejado. |
| VS-M5-03 | AC-M5-002 | Planejado. |
| VS-M6-01 | AC-M6-002 parcial | Planejado. |
| VS-M6-02 | AC-M6-002 parcial | Planejado. |
| VS-M6-03 | AC-M6-001 parcial | Planejado. |
| VS-M6-04 | AC-M6-001 parcial | Planejado. |
| VS-M6-05 | AC-M6-001 parcial | Planejado. |
| VS-M6-06 | AC-M6-002 parcial | Planejado. |
| VS-M7-01 | AC-M7-001 | Planejado. |
| VS-M7-02 | AC-M7-004 | Planejado; a nota antiga cita Pino, substituído por structlog na arquitetura atual. |
| VS-M7-03 | AC-M7-002, AC-M7-003 | Planejado. |
| VS-M7-04 | AC-M7-005 | Planejado. |

M1–M7 continuam não executados. O registro canônico de estados é `docs/process/milestone-status.json`; versões antigas do índice Obsidian e da nota de refresh não são evidência de estado atual. O refresh de 2026-11-11 já estabelece a precedência da especificação do repositório sobre a stack anterior. A preparação de cada marco deve resolver referências OPEN legadas contra `docs/decisions/open-decisions.md`, sem presumir que números antigos ainda apontam para as mesmas decisões.
