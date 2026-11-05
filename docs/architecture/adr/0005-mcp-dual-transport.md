# ADR-005 — MCP stdio + Streamable HTTP; reportes V1

**Status:** Accepted | **Escopo:** V1, salvo indicações explícitas de V2

## Contexto

Diferentes CLIs podem usar transporte e ciclo de vida distintos; o aplicativo precisa auditar resultados relatados.

## Decisão

Implementar stdio primeiro, adicionar HTTP seguro até M4, com Tools/Resources/Prompts compartilhados. V1 permite leitura autorizada e reportes; workflow de aprovação remota só na V2.

## Consequências

Dois adapters e matriz de compatibilidade; reportes não constituem verificação de envio.

## Alternativas consideradas

Stdio exclusivo ou HTTP-only foram rejeitados para V1.

## Verificação

Testes em dois clientes CLI, contratos equivalentes, autenticação HTTP/stdio, dedup reportes.
