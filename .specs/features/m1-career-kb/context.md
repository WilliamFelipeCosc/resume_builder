# M1 — Career KB Core: contexto

**Gathered:** 2026-11-16, America/Sao_Paulo.
**Status:** contexto aprovado para Design em 2026-11-16;
design detalhado aprovado em 2026-11-16 às 17:32 (-03);
tarefas, ferramentas e workers sequenciais aprovados em 2026-11-16 às 20:09 (-03);
início retido por instrução explícita do proprietário.
**Spec:** [spec.md](spec.md).

## Feature Boundary

Entregar AC-M1-001/002/003: cadastro e relações da KB, revisões,
proveniência, privacidade, importação inicial privada por seed, staging,
revisão individual/lote, auditoria e reversão. CI antecede o domínio.
O piloto fictício completo precede a carga privada. M3 continua prioritário.

## Implementation Decisions

Decisões explicitamente escolhidas pelo proprietário nesta conversa:

1. Validar o piloto fictício completo antes de importar o seed privado.
2. Remover por arquivamento, preservando vínculos e histórico.
3. Aceitar uma importação pode manter o fato `unverified`;
   confirmação requer ação explícita separada.
4. Aplicar decisões em lote com semântica tudo ou nada e indicação
   dos itens bloqueantes.
5. Bloquear undo nos itens alterados posteriormente e pedir revisão.
6. Sugerir correspondências ambíguas, exigindo decisão humana
   `create/update/link/ignore`.
7. Editar conteúdo confirmado cria nova revisão com a unidade alterada
   `unverified`, preservando a revisão anterior e exigindo nova confirmação.
   A granularidade foi detalhada na decisão 18.

### Decisões técnicas da entrevista

8. Usar Tailwind CSS com tokens padrão, sem criar uma paleta própria
   para o M1.
9. Usar TanStack Query sobre o cliente OpenAPI gerado para consultas
   e mutações. Chaves, invalidação, retries e ciclo de vida do cache
   serão especificados no design; a biblioteca não substitui o contrato.
10. Usar shadcn/ui, incorporando apenas os componentes necessários,
    com cores padrão do Tailwind. O código incorporado fica sob manutenção
    do projeto. A escolha de primitivas e configuração será documentada
    no design antes da instalação.
11. Usar React Hook Form para formulários, alterações pendentes e erros
    por campo retornados pela API. Pydantic/OpenAPI permanece autoridade
    dos contratos; não acrescentar outra biblioteca de schemas neste momento.
12. Usar React Router em Data Mode, como SPA no Vite, para navegação com
    URLs de cadastro, detalhes, histórico e staging, bloqueio de navegação
    e erros por rota. FastAPI fornece a API. TanStack Query permanece
    responsável pelos dados da API; loaders não implicam execução no servidor.
13. Dividir estado entre TanStack Query (dados da API), React Hook Form
    (rascunhos), URL (filtros compartilháveis) e estado local do React
    (seleção e diálogos), sem store global inicialmente.
14. Organizar o backend por funcionalidade, com separação interna entre
    regras, serviços de aplicação e persistência. API e futuro MCP usam
    os mesmos serviços autorizados.
15. Manter estado atual, revisões imutáveis e auditoria. Undo cria uma
    nova revisão preservando as anteriores; eventos não são a fonte
    canônica para reconstrução obrigatória do estado.
16. Usar arquitetura Feature-based no frontend, por adendo explícito do
    proprietário: funcionalidades reúnem páginas, componentes, hooks e
    integração com API. Componentes genéricos reutilizáveis ficam em área
    compartilhada; regras específicas permanecem na funcionalidade.
17. Usar SQLAlchemy ORM declarativo no novo domínio KB, com modelos
    de persistência internos aos repositórios e DTOs Pydantic na API.
18. Revisar e confirmar por campo no Profile e por entidade nos demais
    registros. Preservar proveniência por campo quando fornecida e permitir
    classificação mais restritiva por campo; Statements são declarações
    individuais. Editar uma unidade confirmada invalida sua confirmação,
    sem transferi-la ao novo conteúdo nem invalidar campos independentes
    do Profile que não foram alterados.
19. Resolver concorrência por revisão-base: rejeitar salvamento obsoleto,
    preservar o rascunho na UI e mostrar diferenças para revisão manual,
    sem mesclar automaticamente campos independentes.
20. Preparar o seed diretamente no M1, com limites explícitos de entrada
    e execução a definir no design. Worker permanece disponível para
    processamento futuro que o justifique; M1 não introduz job de importação
    nem depende de IA ou extração PDF automática.
21. Na execução autorizada da importação, criar cópias imutáveis do PDF
    e do seed no armazenamento privado XDG, verificadas por hash, preservando
    os originais externos. Essa escolha é de comportamento futuro;
    os arquivos reais ainda não foram copiados.
22. Classificar documento, staging e fatos aceitos como `confidential`
    por padrão; alterações de classificação exigem ação explícita na
    revisão. Liberar conteúdo derivado não libera o documento bruto.
23. Paginar listas de KB e staging por offset/limite, com filtros e
    ordenação estável no backend. Limites numéricos, filtros e desempate
    serão apresentados no design.
24. Enviar revisão-base no corpo tipado da operação. Rejeitar versão
    obsoleta com conflito HTTP 409, preservar o rascunho e permitir
    comparação manual. A comparação e a escrita são atômicas no banco;
    lotes validam as revisões dos registros afetados na mesma transação.
    DTOs e nomes dos campos ainda serão definidos no design.
25. Reimportar o mesmo PDF com seed modificado reutiliza a identidade da
    fonte e apresenta as diferenças para revisão humana.
26. Novos vínculos dependentes podem bloquear undo; a seleção de undo
    é atômica e identifica os itens que exigem revisão.
27. Usar tabelas tipadas por entidade para os dados atuais, com histórico
    imutável e metadados por campo. Escolha aprovada durante o início do
    Design, após comparar com registros genéricos em JSON.

Essas escolhas foram aprovadas para o planejamento em 2026-11-16.
Não houve instalação, implementação ou aprovação das demais propostas.

### Agent's Discretion

Não houve delegação geral de decisões de negócio ou schemas. A arquitetura
aprovada permanece FastAPI/Pydantic, SQLAlchemy 2/Alembic, React/Vite e cliente
TypeScript gerado. Detalhes de contrato e implementação serão apresentados
no design antes de executar; não usar o seed como schema persistido implícito.

### Declined / Undiscussed Gray Areas → Assumptions

As propostas ainda não ratificadas estão na tabela de pressupostos da spec.
Não houve recusa explícita de discussão. Design deve apresentar limites,
matriz de permissões, campos/cardinalidades, protocolo de concorrência,
regras de identidade/dedup e coordenação DB/arquivos para revisão.
Entrevista técnica concluída. Schemas, limites e matriz de permissões
serão apresentados no design, sem supor campos de negócio ou cardinalidades.

As propostas de reimportação e dependências/atomicidade de undo foram
ratificadas na revisão da consolidação. O design detalhado também foi
aprovado, incluindo campos/cardinalidades, permissões, budgets e dependências
propostas. A implementação do marco continua NOT_RUN; compatibilidade de
versões ainda exige o spike descrito nas tarefas.

## Specific References

- Obsidian: `10 Projects/Personal/Resume Builder/Vertical Slices/M1.md`,
  lido em 2026-11-16. VS-M1-01/02/03 detalham CRUD, relações e revisão;
  importação/staging/undo constam do objetivo/Done, sem passos próprios.
- Repo: `PROJECT_SOURCE.md` §4.1, `docs/modules/career-kb.md`,
  `docs/contracts/career-kb.md`, `docs/product/requirements.md`,
  `docs/roadmap/acceptance-criteria.md`, ADR-003/007/014.
- Localização privada informada pelo proprietário:
  `/home/williamf/Documentos/Projects/resume_builder_spec/private/imports/`.
  Os originais foram apenas lidos; não foram copiados para o repositório.

### Inspeção estrutural real, sem confirmação de veracidade

Arquivos localizados: `Curriculo.pdf`, `career_kb_seed.json` e
`resume_document_seed.json`. Apenas o seed KB e metadados do PDF foram
inspecionados; o seed de currículo permanece reservado ao M2.

- Schema KB: `career-kb-import-v0.1`; envelope `staged_pending_review`.
- Um SourceDocument; hash SHA-256 e contagem de páginas conferem com o PDF
  presente. PDF com uma página e assinatura `%PDF-`.
- IDs únicos; 71 referências de fonte/página estruturalmente válidas;
  58 vínculos entre entidades apontam para IDs existentes.
- 56 marcações `review_status` com valor `pending_review`.
- Coleções: 4 experiências, 12 statements, 2 formações, 27 skills/termos,
  3 idiomas, 1 projeto e 2 realizações; um Profile.
- Profile contém valores/proveniência por campo; campos desconhecidos
  podem ser nulos. Education distingue atualidade histórica de atualidade
  presente. Skills distinguem listagem explícita de menção.
- Não existe coleção `Evidence` separada no seed. A representação de
  evidências no domínio deve ser projetada explicitamente; uma referência
  de fonte não constitui comprovação independente de uma declaração.
- As verificações não comparam semanticamente todos os trechos ao PDF,
  não validam qualificações e não equivalem a aceite do conteúdo.

Nenhum valor pessoal, trecho do currículo ou hash foi reproduzido aqui.
Esta inspeção não constitui suíte de testes do M1 nem teste do futuro adapter.

## Definição adicional aprovada — fonte manual

Em 2026-11-17 às 08:56 (-03), o proprietário aprovou explicitamente o
contrato que faltava em T16: `text` obrigatório, até 8.000 caracteres;
`title` opcional, até 256 caracteres; `idempotencyKey` UUID. Guardar o texto
em UTF-8 como objeto imutável por hash no armazenamento privado existente,
com classificação inicial `confidential`. A anotação é uma fonte declarada
pelo usuário e não confirma qualificações. O título é metadado privado.
O corpo não permite escolher principal, clearance ou caminho de disco.
Essa decisão complementa o design aprovado e libera T16.

## Refinamento aprovado — tipos e envelopes de T18

Em 2026-11-17 às 09:12/09:13 (-03), o proprietário escolheu metricValue
como texto opcional preservado, sem conversão numérica, e aprovou os
tipos e formatos de [contracts-refinement.md](contracts-refinement.md).
Incluem rótulos como lista de textos, categorias/unidades textuais sem
taxonomia, PartialDate com value/precision, envelopes de criação tipados,
fieldPrivacy e leitura com restrictedFields e confirmação na granularidade
já aprovada. Essa decisão fecha a lacuna de T18, sem novos campos de
qualificação nem promoção automática de conteúdo.

## Deferred Ideas

Importadores completos PDF/DOCX/Obsidian/GitHub/LinkedIn, embeddings,
editor avançado, MCP real da KB e distribuição permanecem nos marcos
previstos. M1 não depende de provider de IA nem extrator PDF novo.

## Aprovação das tarefas e retenção do início

Em 2026-11-16 às 20:09 (-03), o proprietário aprovou todas as tarefas e
ferramentas, escolheu workers sequenciais por lote e instruiu: não iniciar
ainda. Preservar as aprovações; aguardar somente comando explícito de início.
Não despachar agentes, executar T1, instalar dependências, rodar experimentos
ou iniciar implementação enquanto essa retenção estiver vigente.
