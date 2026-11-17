# M1 — refinamento proposto dos contratos T18

**Status:** aguardando decisão humana; não é contrato executável aprovado.
**Data:** 2026-11-17. Complementa os campos de negócio de `design.md` sem
criar taxonomias, qualificações ou confirmação automática.

## Tipos ainda ausentes do design

- `originalLabels`: lista de textos, cada rótulo com até 256 caracteres.
- `category`, `metricType` e `metricUnit`: texto opcional até 256 caracteres;
  sem enums ou conversão para uma taxonomia não aprovada.
- `metricMeaning`: texto opcional até 8.000 caracteres.
- `metricValue`: proposta de texto opcional até 8.000 caracteres, preservado
  sem conversão numérica ou inferência. Alternativa: decimal informado
  explicitamente, sem extrair números automaticamente de narrativa.
- `PartialDate`: `{value: string, precision: 'year'|'month'|'day'}`, com
  formato ISO válido e coerente com a precisão; texto original permanece
  em seu campo próprio. Datas e atualidade desconhecidas continuam null.

Os demais campos seguem os nomes, obrigatoriedade e semântica do design:
textos/nome, listas de rótulos e booleanos históricos, sem coerção silenciosa.
DTOs são concretos para os nove tipos, com aliases camelCase e extra=forbid.

## Criação por tipo

```text
{
  content: <DTO concreto do tipo>,
  sourceDocumentId: UUID,
  profileId: UUID | null,
  idempotencyKey: UUID,
  privacy: public | professional | confidential | secret,
  fieldPrivacy: {<campo permitido do DTO>: <classificação>}
}
```

`profileId` é null somente para Profile e obrigatório nos demais tipos.
Privacidade inicial sugerida confidential; mudanças são explícitas e
classificação de campo pode apenas restringir a da entidade. O mapa de
campos é fechado pelos nomes permitidos de cada DTO, com default vazio.
A criação gera IDs/revisões e estado unverified no servidor; o cliente não
escolhe confirmação, principal ou clearance. A fonte fornecida é verificada
e sua classificação permanece independente da do fato.

## Leitura e listagem

```text
{
  id: UUID,
  revisionId: UUID,
  content: <DTO concreto de leitura com campos nullable>,
  restrictedFields: [<campo permitido>],
  privacy: <classificação>,
  confirmation: confirmed | unverified
}
```

Para Profile, `fieldConfirmations: {<campo>: confirmed | unverified}`
substitui confirmação por entidade. `restrictedFields` distingue um valor
desconhecido de um campo omitido por privacidade; o SQL não recupera o
conteúdo restrito. Fontes e metadados históricos preservam os nomes do
modelo aprovado e só aparecem quando autorizados.

Listagens seguem `{items, offset, limit, total}`, como no design.
Os comandos de escrita que alteram estado recebem `baseRevisionId` e
`idempotencyKey` conforme o protocolo já aprovado. A aprovação desta
proposta não autoriza novas operações ou mudanças nos campos de negócio.
