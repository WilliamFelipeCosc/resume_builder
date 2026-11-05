# ADR-004 — MCP-first, sem browser integrado

**Status:** Accepted | **Escopo:** V1, salvo indicações explícitas de V2

## Contexto

O usuário deseja execução pelo Hermes/Codex/Claude Code/Kimi na própria CLI, evitando que o aplicativo controle navegador.

## Decisão

Remover browser automation, Chrome/CDP manager, Hermes browser executor e UI de screenshots internos. O aplicativo fornece contexto pelo MCP; agentes CLI externos navegam e preenchem.

## Consequências

Portabilidade entre agentes; observabilidade limitada a tool calls/reportes; sem controle técnico de ações do agente fora do MCP.

## Alternativas consideradas

Execução integrada com Playwright/Hermes no Worker foi explicitamente descartada.

## Verificação

M0.5: agente CLI externo preenche formulário fake a partir de MCP, e nenhum módulo do app contém executor navegador.
