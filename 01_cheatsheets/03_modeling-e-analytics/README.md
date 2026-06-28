# Modeling e Analytics

Guias de referencia rapida para Analytics Engineering, modelagem dimensional e consumo analitico em BI.

## Indice
- [Como usar esta pasta](#como-usar-esta-pasta)
- [Ordem sugerida de leitura](#ordem-sugerida-de-leitura)
- [Mapa dos cheatsheets](#mapa-dos-cheatsheets)
- [Escopo da pasta](#escopo-da-pasta)
- [Como isso se conecta com o repositorio](#como-isso-se-conecta-com-o-repositorio)

## Como usar esta pasta
Esta pasta cobre a camada entre engenharia de dados e consumo analitico.

Use este modulo para responder perguntas como:
- como modelar para BI sem destruir performance
- quando usar fato transacional, snapshot ou acumulativa
- quando uma dimensao precisa historizacao
- o que materializar no banco e o que deixar para a camada semantica
- como expor um modelo mais seguro e amigavel para consumo

Ela funciona melhor como apoio de decisao e modelagem do que como leitura puramente tecnica de implementacao.

## Ordem sugerida de leitura

### Fundamentos de modelagem
1. [`01_modelagem-dimensional.md`](01_modelagem-dimensional.md)
2. [`02_tipos-tabelas-fato.md`](02_tipos-tabelas-fato.md)
3. [`03_slowly-changing-dimensions.md`](03_slowly-changing-dimensions.md)

### Consumo e camada semantica
4. [`04_camada-semantica-e-dax.md`](04_camada-semantica-e-dax.md)
5. [`05_otimizacao-bi.md`](05_otimizacao-bi.md)
6. [`06_boas-praticas-consumo.md`](06_boas-praticas-consumo.md)

## Mapa dos cheatsheets

### Fundamentos de modelagem
- [`01_modelagem-dimensional.md`](01_modelagem-dimensional.md): star schema, snowflake, OBT e trade-offs de modelagem.
- [`02_tipos-tabelas-fato.md`](02_tipos-tabelas-fato.md): tipos de fato, escolha de grao e natureza das medidas.
- [`03_slowly-changing-dimensions.md`](03_slowly-changing-dimensions.md): SCD, surrogate keys, historizacao e riscos de modelagem temporal.

### Camada semantica e consumo
- [`04_camada-semantica-e-dax.md`](04_camada-semantica-e-dax.md): criterios para decidir entre SQL/Gold, semantic layer e calculo no BI.
- [`05_otimizacao-bi.md`](05_otimizacao-bi.md): trade-offs entre importacao, DirectQuery, cardinalidade e relacoes complexas.
- [`06_boas-praticas-consumo.md`](06_boas-praticas-consumo.md): nomenclatura, exposicao de campos, ocultacao de chaves e ergonomia do modelo final.

## Escopo da pasta
O foco atual desta area esta mais proximo de:
- modelagem dimensional classica
- Analytics Engineering orientado a BI
- consumo em Power BI, Tableau, Metabase e ferramentas similares

Nao e uma pasta de implementacao SQL/PySpark. Ela complementa essas areas discutindo:
- desenho do modelo
- semantica
- governanca de consumo
- trade-offs entre performance, usabilidade e manutencao

## Como isso se conecta com o repositorio
Esta pasta conversa diretamente com:

- SQL: [`../sql/`](../sql)
  Porque varias decisoes de modelagem impactam joins, granularidade, nulos, snapshots e camada Gold.

- PySpark: [`../pyspark/`](../pyspark)
  Porque muitas dessas decisoes precisam ser implementadas em pipelines, Delta e cargas incrementais.

- Contexto de negocio: [`../../07_contexto-negocio/`](../../07_contexto-negocio)
  Porque a modelagem correta depende de regra de negocio, semantica de indicador e forma de consumo.

- Revisao e evolucao: [`../../06_revisao-evolucao/`](../../06_revisao-evolucao)
  Onde ficam registradas avaliacoes e pontos de melhoria desta area.
