# ADR-013 — Documentação modular e consolidada

**Status:** Accepted | **Escopo:** V1, salvo indicações explícitas de V2

## Contexto

O projeto precisa servir de base para ChatGPT Project e múltiplos agentes de programação.

## Decisão

`PROJECT_SOURCE.md` autocontido, módulos em docs, ADRs, REQ/AC e AGENTS.md agnóstico; rastreabilidade leve sem ritual SDD/EDD obrigatório.

## Consequências

Exige sincronização do documento principal com alterações modulares, mas reduz acoplamento e contexto desnecessário.

## Alternativas consideradas

Monólito documental exclusivo ou metodologia formal SDD/EDD mandatória foram rejeitados.

## Verificação

Links internos, IDs REQ/AC e changelog de decisão revisados em mudanças estruturais.
