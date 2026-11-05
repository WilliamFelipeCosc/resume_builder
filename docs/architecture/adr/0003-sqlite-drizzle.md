# ADR-003 — SQLite + Drizzle

**Status:** Accepted | **Escopo:** V1, salvo indicações explícitas de V2

## Contexto

Aplicação pessoal com entidades relacionadas, operações majoritariamente locais e necessidade de backups portáteis.

## Decisão

Persistência principal em SQLite/Drizzle, modo WAL e migrations; documentos binários no filesystem XDG.

## Consequências

Controle de escritores e backups consistentes; Redis não guarda fatos canônicos.

## Alternativas consideradas

Prisma ou PostgreSQL não serão dependências da V1.

## Verificação

Testes de transações, migrations, concorrência básica e restore com manifest.
