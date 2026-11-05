# Persistência, backup, restore e portabilidade

**DECIDED:** SQLite/Drizzle + arquivos XDG; Redis é fila operacional, não banco de verdade. Backups automáticos locais e exportações portáteis na V1.

## Backup

Snapshot consistente do SQLite em WAL (não copiar apenas `.db` vivo sem o método apropriado), inventário dos anexos/documentos, hashes, manifesto de versão, opcional criptografia, retenção configurável e verificação periódica. Backup preventivo antes de migrations destrutivas. Não incluir keyring, cookies, perfil Chrome, cache Redis e traces de depuração por padrão.

## Restore

Validar hash e versão → bloquear novas gravações → restaurar em diretório temporário → rodar integridade e migrations controladas → promover artefato validado e manter rollback → reconciliar tasks pendentes com SQLite/BullMQ. Relatos de submissão com estado incerto não originam reenvios automáticos.

## Portabilidade

Export JSON versionado da Career KB/metadata, Markdown para narrativas, CSV para vagas/candidaturas, PDF/DOCX/HTML para currículos. Importação usa validação/schema e revisão Staging Area, enquanto restore completo usa mecanismo de snapshot próprio para preservar IDs/relações.

## Diretórios

`~/.config/resume-agent`, `~/.local/share/resume-agent`, `~/.cache/resume-agent`, `~/.local/state/resume-agent` (nomes sujeitos a identidade final do produto). Arquivos com permissões adequadas e sem inclusão automática no repositório.
