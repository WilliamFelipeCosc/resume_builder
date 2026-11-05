# ADR-008 — Recuperação híbrida V1, RAG avançado V2

**Status:** Accepted | **Escopo:** V1, salvo indicações explícitas de V2

## Contexto

Contextos grandes são caros e podem conter evidências irrelevantes; recuperação por só palavras-chave pode perder sinônimos.

## Decisão

Começar SQL relacional e FTS5/BM25; completar embeddings + fusão na V1. Final V2: RAG avançado para aprendizado/benchmarks. Preferir embeddings locais se viáveis.

## Consequências

Devem existir adapters/versões de índice, avaliação de relevância e limites de tokens; busca semântica não prova fato.

## Alternativas consideradas

RAG avançado como requisito de M3 foi rejeitado por impacto no roadmap.

## Verificação

Baseline FTS vs híbrido em dataset, sem vazamento de fontes privadas.
