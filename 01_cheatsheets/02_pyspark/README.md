# Cheatsheets PySpark

Guias de referência rápida para PySpark com foco em Databricks / Spark e em tarefas frequentes da rotina de engenharia de dados.

## Índice
- [Como usar esta pasta](#como-usar-esta-pasta)
- [Ordem sugerida de leitura](#ordem-sugerida-de-leitura)
- [Mapa dos cheatsheets](#mapa-dos-cheatsheets)
- [Como isso se conecta com practice](#como-isso-se-conecta-com-practice)
- [Quando ir para recipes](#quando-ir-para-recipes)

## Como usar esta pasta
Esta pasta funciona melhor como material de consulta rápida do que como leitura linear completa. A sequência ideal costuma ser:

1. consolidar a base de execução e DataFrame API
2. consultar transformações analíticas conforme o problema
3. usar os blocos de Delta, dbutils, quality e performance quando a discussão já estiver em contexto Databricks ou produção

## Ordem sugerida de leitura

### Base operacional
1. [`01_fundamentos-dags-sql.md`](01_fundamentos-dags-sql.md)
2. [`02_leitura-escrita-io.md`](02_leitura-escrita-io.md)
3. [`03_exploracao-e-tipagem.md`](03_exploracao-e-tipagem.md)
4. [`04_transformacoes-e-df-api.md`](04_transformacoes-e-df-api.md)
5. [`05_nulos-e-condicionais.md`](05_nulos-e-condicionais.md)

### Transformação analítica
6. [`06_agrupamentos-e-pivots.md`](06_agrupamentos-e-pivots.md)
7. [`07_joins-relacionais.md`](07_joins-relacionais.md)
8. [`08_window-functions.md`](08_window-functions.md)
9. [`09_json-structs-schemas.md`](09_json-structs-schemas.md)

### Databricks / Operação
10. [`10_delta-lake-api.md`](10_delta-lake-api.md)
11. [`11_dbutils-workspace.md`](11_dbutils-workspace.md)
12. [`12_data-quality-operacional.md`](12_data-quality-operacional.md)
13. [`13_performance-e-arquitetura.md`](13_performance-e-arquitetura.md)
14. [`14_medallion-architecture.md`](14_medallion-architecture.md)

## Mapa dos cheatsheets

### Fundamentos operacionais
- [`01_fundamentos-dags-sql.md`](01_fundamentos-dags-sql.md): lazy evaluation, DAG, actions, DataFrame API e ponte com Spark SQL.
- [`02_leitura-escrita-io.md`](02_leitura-escrita-io.md): leitura de arquivos, schema explícito, JDBC e gravação com particionamento.
- [`03_exploracao-e-tipagem.md`](03_exploracao-e-tipagem.md): `printSchema`, `describe`, cast, datas, timestamps e tipagem.
- [`04_transformacoes-e-df-api.md`](04_transformacoes-e-df-api.md): `select`, `withColumn`, `selectExpr`, filtros, `dropDuplicates`, `unionByName`, `sample` e regex.
- [`05_nulos-e-condicionais.md`](05_nulos-e-condicionais.md): `when`, `coalesce`, `fillna`, `dropna` e cuidados com nulos.

### Transformação analítica
- [`06_agrupamentos-e-pivots.md`](06_agrupamentos-e-pivots.md): agregações, pivots e sumarização analítica.
- [`07_joins-relacionais.md`](07_joins-relacionais.md): joins, ambiguidades, anti/semi join e broadcast.
- [`08_window-functions.md`](08_window-functions.md): ranking, deduplicação, lag/lead e janelas temporais.
- [`09_json-structs-schemas.md`](09_json-structs-schemas.md): JSON, structs, explode, `from_json`, `schema_of_json` e schema enforcement.

### Databricks e produção
- [`10_delta-lake-api.md`](10_delta-lake-api.md): Delta Lake API, `merge`, time travel, restore, optimize e vacuum.
- [`11_dbutils-workspace.md`](11_dbutils-workspace.md): `dbutils`, widgets, secrets e automação em notebooks Databricks.
- [`12_data-quality-operacional.md`](12_data-quality-operacional.md): checks de grão, nulos, chaves e reconciliação pós-join.
- [`13_performance-e-arquitetura.md`](13_performance-e-arquitetura.md): AQE, repartition/coalesce, skew, pandas UDFs, arquitetura e testes.
- [`14_medallion-architecture.md`](14_medallion-architecture.md): papel de Bronze, Silver e Gold, granularidade, colunas técnicas e critérios de desenho de camada.

## Como isso se conecta com practice
Os cheatsheets de PySpark funcionam como base de apoio para estudo e futura expansão prática do repositório em [`../../practice/`](../../practice).

Mesmo que o MVP atual de prática esteja focado em SQL, esta pasta ajuda a:
- aprofundar o raciocínio de pipeline e transformação
- comparar abordagens entre SQL e DataFrame API
- apoiar evolução futura de exercícios e revisões em Spark

Para navegar no módulo prático:
- workflow: [`../../practice/WORKFLOW.md`](../../practice/WORKFLOW.md)

## Quando ir para recipes
Se você já sabe o problema que quer resolver e quer um exemplo pronto para adaptar, vá para [`../../02_recipes/pyspark/`](../../02_recipes/pyspark).

Casos comuns:
- tratar nulos
- deduplicar dados
- otimizar joins
