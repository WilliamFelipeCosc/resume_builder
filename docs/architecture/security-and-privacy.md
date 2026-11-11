# Segurança, privacidade e confiabilidade

**Obrigatório desde M0:** local-first não equivale a dados sempre locais; qualquer provider remoto precisa de autorização e minimização antes do envio.

## Políticas de dados

| Classe | Exemplo | Regras gerais |
|---|---|---|
| public | nome profissional deliberadamente público | acesso conforme finalidade |
| professional | experiências confirmadas compartilháveis | liberar por escopo/candidatura |
| confidential | documentos internos, contatos privados, salários não públicos | negar por padrão; opt-in específico |
| secret | tokens, credenciais, segredos de terceiros | nunca compartilhar com LLM/MCP; usar keyring |

PDF pessoal e seeds são **privados por padrão**, permanecem `pending_review` e não entram em CI/Git. `private/` excluído no `.gitignore`. Classificação deve ser granular por campo/entidade e não só pelo documento pai.

## Fronteiras

- HTTP FastAPI/MCP: bind loopback, auth adequada, Host/Origin, CSRF quando aplicável, proteção contra DNS rebinding, limites de tamanho/rate limit, CORS restritivo, nenhum bypass por ambiente de desenvolvimento.
- `stdio`: logs em stderr, stdout reservado ao protocolo; subprocessos sem capacidades ou segredos desnecessários.
- Importadores: sniff do conteúdo, limites de tamanho/tempo, path traversal/symlink e zip bomb, isolamento de parser/Chromium, tratamento de arquivos hostis.
- IA: entrada de anúncio, markdown, imagem e MCP como dado não confiável; não executar instruções embutidas; provider escolhido explicitamente, sem fallback pago.
- Worker: timeouts, dedupe e retries com chaves idempotentes, não expor payload privado no Redis além do mínimo, sanitização de exceptions.
- Segredos via Linux keyring (Secret Service), falha segura se indisponível sem aprovação de alternativa.

## Auditoria e estados

Separar `reported_by_agent`, `confirmed_by_user`, `verified_by_evidence`. Relato `reported_submitted` não significa confirmação de candidatura. `ChangeSet` só altera revisão aprovada; fatos canônicos só com ação explícita de revisão.

## Observabilidade e backups

`structlog` JSON e OpenTelemetry, Sentry desabilitado por padrão. Não registrar prompt bruto, currículo, cookies, conteúdo de screenshot ou tokens em logs/traces. Backup consistente de SQLite/WAL + arquivos, checksum/manifest, retenção e restore testado; excluir credenciais e cache Redis.

## Testes negativos e gates

Privacidade em dados de teste sintéticos; tentativas de injection em vagas e MCP; idempotência/replay, SQL injection, escopo cruzado, Unicode/caminhos, PDFs inválidos, vazamento em logs; exportação incorreta deve bloquear release. Nenhum teste faz submissão real.
