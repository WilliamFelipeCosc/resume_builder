# Segurança, privacidade e threat boundaries

**REQ-SEC-001..002 — DECIDED.** Local-first não equivale a offline. Dados podem seguir a providers remotos **apenas** após avaliação de política por tarefa e classificação.

## Classificação

`public`, `professional_shareable`, `confidential`, `sensitive_secret`. Documentos importados são privados por padrão, inclusive até serem revisados. Contexto e evidências expostos por API/MCP devem passar pelo mesmo `ContextPolicyEngine` com `clientId`, `applicationId`, `purpose`, `operation`, `dataClassification` e consentimento permitido.

## Credenciais e execução

Usar Secret Service/keyring Linux quando disponível; nunca registrar tokens/cookies em SQLite, prompts, traces ou backup. Para cenários sem keyring, exigir configuração de alternativa explicitamente aprovada e com falha segura. Secrets jamais em logs de stdout MCP.

API/HTTP MCP no `127.0.0.1`; autenticação de sessão e tokens/capabilities, validação Origin/Host, proteção contra CSRF e DNS rebinding, payload/rate limits e CORS restrito. `stdio` não é automaticamente seguro: herda contexto local; limitar acesso e funcionalidades por cliente, não confiar só na identidade do processo.

Redis em rede local restrita, portas de debug privadas, permissões XDG restritivas. Tauri precisa aplicar política de capabilities, validação de comandos, CSP e proteção contra abertura de conteúdo não confiável (PROPOSED detalhes).

## Segurança dos agentes

- **Não** existe agente navegador integrado. Cliente CLI usa browser e ferramentas próprios; a política MCP não controla cliques fora do servidor.
- Nenhuma ferramenta `submit_application`, `run_command`, `read_any_file`, `query_sql`, `get_secret`.
- Usuário aprova/realiza envio final **no executor externo** por padrão. O app apenas instrui e registra relato, sem prometer garantia técnica.
- Proteção contra prompt injection: descrições de vagas, texto de terceiros, screenshots e documentos importados têm papel de dados, não de instruções de sistema.

## Telemetria

Pino/OTel/Sentry coletam IDs, status, duração e métricas. Sentry Cloud é opt-in e deve filtrar eventos **antes do envio**; não coletar prompts/respostas/PII, screenshots ou documentos por padrão. Jaeger local opcional. Logs/auditoria são separados.

## Testes negativos mínimos

- Cliente sem permissão não lê evidência confidencial (mesmo via search, MCP Resource ou erro detalhado).
- Injeção no texto da vaga não eleva privilégio nem altera permissões.
- Token inválido, Origin/Host divergente e payload excessivo são rejeitados.
- Relato de submissão do agente não altera estado para confirmado sem revisão/critério verificável.
- Mudança via IA não grava fato confirmado sem aprovação.
