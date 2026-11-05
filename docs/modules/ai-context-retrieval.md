# Recuperação de contexto e evidências

**REQ-CTX-001 — DECIDED.** Recuperação híbrida completa na V1; RAG avançado ao fim da V2 para aprendizado/benchmarking.

## Fases

- M1–M2: consultas SQL e resolução por IDs/relações, fonte canônica e política de privacidade.
- M3: FTS5/BM25 inicial e matches explícitos com evidências; suficientes para primeiro fluxo útil.
- M4: exposição pelo MCP com `contextScope`, `maxItems`, `tokenBudget`, `truncated`, referências e acesso progressivo.
- M6: embeddings + busca semântica + fusão com consultas relacionais/FTS; model/version/dimensions, reindexação e métricas de qualidade.
- V2 final: query rewriting, decomposition, rerankers dedicados, pesquisa adaptativa, comparação de modelos e curvas qualidade/custo/latência.

## Pipeline

`ContextPolicy` determina o universo autorizado **antes** de buscar. Consulta estruturada + BM25 + vetorial → dedup por entidade/versão → fusão (RRF ou similar, PROPOSED) → reranking permitido → resumo baseado em evidência → pacote com proveniência e limite de tokens. Não inferir `verified` a partir de alta similaridade.

## Embeddings

Provider local preferível quando possível, remoto opcional e com autorização. Não misturar vetores de modelos/dimensões diferentes. Cache versionado por hash de conteúdo, modelo e política; reindexar na alteração do conteúdo/modelo. `sqlite-vec` pode ser avaliado, mas é opção experimental substituível; índice separado também é possível mediante ADR.

## Estratégia de chunking

Entidades pequenas mantidas inteiras; documentos longos divididos por semântica/seção/página, mantendo offsets, versão e IDs de origem. Fatos canônicos não se tornam meros chunks de texto.

## Avaliações

Conjunto de consultas anotadas: recall@k, precision@k, MRR/nDCG quando pertinentes, evidências corretas, taxa de omissão, latência, tokens e custo real/estimado (se disponível). Comparar SQL+FTS e híbrido sobre mesmo corpus antes de escolher pesos. RAG V2 só é adotado se ganhos forem mensuráveis ou houver objetivo educacional declarado.
