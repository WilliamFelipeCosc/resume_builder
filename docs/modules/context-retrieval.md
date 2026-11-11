# Career Context Retrieval

## M3: SQL + FTS5/BM25

Vínculos relacionais fortes (projeto→experiência→skill→evidência) e busca full-text FTS5/BM25. Aplicar política e status de confirmação **antes** da seleção/ranking e novamente antes do envio a provider/MCP. Exibir `sourceId`, trecho, versão e evidência ou desconhecido. Similaridade não comprova qualificação.

## M6: híbrido e embeddings

Adicionar embeddings (preferência local quando viável) e retrieval híbrido SQL+FTS+vetor. Modelos, versões, dimensão, autorização e vetor index versionados; não misturar espaços vetoriais entre provedores. Fusão/ranking e latência medidos em corpora representativos e sintéticos, não score arbitrário.

## MCP e economia de contexto

Respostas progressivas por resumo/IDs, detalhes sob demanda, orçamento de tokens, `truncated=true` e motivos explícitos quando houver corte. Escopos restritos à candidatura; nenhuma busca geral indiscriminada por toda a KB.

## V2 final — pesquisa avançada

Query rewriting, decomposição, reranking, estratégias adaptativas, benchmarks comparativos. Essas técnicas não são pré-requisito de M3.

## Métricas e validações

Recall/precision por requisito, evidências incorretas, latência, tokens/custo estimado quando confiável, e vazamento de dados. Metas finais são open decision; não inventar thresholds. Tests devem cobrir entidade com mesma palavra mas evidência insuficiente e acesso negado.
