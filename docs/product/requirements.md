# Requisitos funcionais rastreáveis

Status: `DECIDED` salvo quando marcado de outro modo. A implementação deve vincular testes e critérios de aceite a cada ID.

| ID | Requisito | Versão |
|---|---|---|
| REQ-KB-001 | Criar/editar Experience, Project, Achievement, Skill e Evidence relacionados | M1 |
| REQ-KB-002 | Manter proveniência, status de confirmação, versões e privacidade | M1→V1 |
| REQ-KB-003 | Importar PDF, DOCX, MD, TXT, JSON, diretórios, Obsidian, GitHub e exportações LinkedIn | V1 |
| REQ-KB-004 | Staging Area e revisão de propostas de ingestão/dedup/conflitos | V1 |
| REQ-RES-001 | Gerar ResumeDocument estruturado a partir da Career KB | M2 |
| REQ-RES-002 | Preview + template ATS + exportação PDF, histórico/revisão | M2 |
| REQ-RES-003 | Editor inline/drag-drop, estilo, templates e preview paginado | V1 |
| REQ-RES-004 | ChangeSets com diff, aprovação e rollback | M3 mínimo→V1 |
| REQ-RES-005 | Exportar PDF ATS/visual, DOCX e HTML com validação | V1 |
| REQ-JOB-001 | Importar anúncios por URL, texto e screenshot | M3 |
| REQ-JOB-002 | Extrair requisitos/categorias, preservar snapshot original | M3 |
| REQ-JOB-003 | Matching explicável com evidências e lacunas | M3 |
| REQ-AI-001 | Providers Hermes default e OpenAI manual, sem fallback pago automático | M3→V1 |
| REQ-AI-002 | IA contextual inline, depois chat e sugestões por eventos | V1 |
| REQ-ANS-001 | Reusar respostas aprovadas, gerar sugestão fundamentada e classificar sensibilidade | M5 |
| REQ-MCP-001 | MCP stdio consulta contextos autorizados e recebe reports | M0.5 spike→M4 |
| REQ-MCP-002 | Streamable HTTP + schemas/versionamento/segurança por capacidade | M4 |
| REQ-MCP-003 | Expor resposta opcional por AI Service e provenance | M4→M5 |
| REQ-APP-001 | Histórico básico, etapas externas manuais, registros de progresso não verificados | M5 |
| REQ-CTX-001 | SQL + FTS5/BM25, embeddings + fusão e progressive context loading | M3→V1 |
| REQ-SEC-001 | Política de privacidade antes de enviar dados ao MCP/provider | Desde M0 |
| REQ-SEC-002 | Keyring, loopback, autenticação/origem/host, auditoria e rate limits | V1 |
| REQ-DATA-001 | Backups locais automáticos, restore verificado e exportação portátil | V1 |
| REQ-OPS-001 | Pino, OTel, Jaeger opcional, Sentry opt-in e métricas de agentes | V1 |
| REQ-LIN-001 | Distribuir Web local e Tauri/RPM com instalação manual assistida | V1 |
| REQ-QA-001 | Quality Gates, AI Evals e testes de contratos MCP com dois clientes | V1 |
| REQ-V2-001 | Descoberta automática de vagas | V2 |
| REQ-V2-002 | Notificações/follow-ups e tracking ampliado | V2 |
| REQ-V2-003 | Approval workflow formal via MCP | V2 |
| REQ-V2-004 | Pipeline RAG avançado e benchmarks de aprendizado | Final V2 |

Critérios verificáveis: [acceptance-criteria.md](../roadmap/acceptance-criteria.md).
