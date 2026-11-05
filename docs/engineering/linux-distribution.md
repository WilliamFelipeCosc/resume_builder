# Execução e distribuição Linux

**DECIDED:** desenvolvimento Web/Vite primeiro; V1 completa inclui Tauri, RPM, opção de acesso pelo browser. Instalação **manual assistida**, não gestão automática de dependências externas.

## Desenvolvimento

pnpm Workspaces/Turborepo coordenam API/Web/Worker/MCP; Redis iniciado manualmente no Compose com AOF e healthcheck; RabbitMQ `profile` experimental. Hermes/OpenAI provider e agentes CLI configurados separadamente; app não instala Chrome/agents automaticamente.

## Distribuição

Tauri reutiliza frontend React e acessa API local. WebKitGTK para UI Tauri não se confunde com browser utilizado por agentes CLI. RPM priorizado para Fedora/Nobara; AppImage `PROPOSED` opcional. Considerar empacotar runtimes Node para produção: escolha técnica aberta a spike, não pressupor Node global instalado. Redis/serviços externos são pré-requisitos documentados.

## Services

Unidades `systemd --user` opcionais para API/Worker, ativadas manualmente; modo sob demanda por padrão. CLI `resume-agent doctor` apenas diagnostica versão/saúde de SQLite, Redis, provider, MCP/transporte, keyring e filesystem sem modificar o sistema. Setup manual assistido inclui documentação e checagens, não wizard obrigatório que execute instalações privilegiadas.

## Segurança de integração

Loopback para APIs, keyring Linux e permissões dos diretórios. O app não gerencia browser/CDP; ferramentas de browser e perfis pertencem às CLIs externas. Nunca confundir a interface Tauri com Chrome.
