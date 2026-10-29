# Cheatsheets PySpark

Referência rápida da DataFrame API e do ecossistema Spark/Databricks para pipelines batch. Streaming não faz parte do escopo atual.

## Ordem sugerida

1. [Fundamentos, DAGs e SQL](01_fundamentos-dags-sql.md)
2. [Leitura e escrita](02_leitura-escrita-io.md)
3. [Exploração e tipagem](03_exploracao-e-tipagem.md)
4. [Transformações e DataFrame API](04_transformacoes-e-df-api.md)
5. [Nulos e condicionais](05_nulos-e-condicionais.md)
6. [Agrupamentos e pivots](06_agrupamentos-e-pivots.md)
7. [Joins](07_joins-relacionais.md)
8. [Window functions](08_window-functions.md)
9. [JSON, structs e schemas](09_json-structs-schemas.md)
10. [Delta Lake API](10_delta-lake-api.md)
11. [DBUtils e workspace](11_dbutils-workspace.md)
12. [Data quality operacional](12_data-quality-operacional.md)
13. [Performance, arquitetura e testes](13_performance-e-arquitetura.md)
14. [Arquitetura Medallion](14_medallion-architecture.md)

## Como consultar

- Prefira funções Spark nativas antes de UDFs.
- Valide schema, grão, cardinalidade e volume antes de otimizar.
- Use `explain()` e métricas da Spark UI para confirmar hipóteses de performance.
- Trate números de partições, limites de broadcast e políticas Delta como configurações dependentes do workload.

[Voltar ao README principal](../../README.md)

