# Cheatsheets SQL

Referência rápida de Spark SQL/Databricks SQL para transformação e operação de dados. Os exemplos devem ser adaptados ao catálogo, ao volume e ao Databricks Runtime do projeto.

## Ordem sugerida

1. [Sintaxe básica](01_sintaxe-basica.md)
2. [Tipos e formatos](02_tipos-e-formatos.md)
3. [Sanitização e nomenclatura](03_sanitizacao-e-nomenclatura.md)
4. [Nulos e condicionais](04_nulos-e-condicionais.md)
5. [CTEs](05_ctes.md)
6. [Group By e pivots](06_group-by-e-pivots.md)
7. [Joins](07_joins.md)
8. [Window functions](08_window-functions.md)
9. [JSON e structs](09_json-structs.md)
10. [Delta DML](10_delta-dml.md)
11. [Data quality e profiling](11_data-quality-profiling.md)
12. [Performance tuning](12_performance-tuning.md)

## Como consultar

- Comece pelo exemplo mínimo e confirme o resultado em uma amostra controlada.
- Leia os cuidados antes de aplicar operações destrutivas, hints ou otimizações físicas.
- Para joins, declare e valide o grão esperado de cada lado.
- Para datas, timestamps e Delta Lake, confirme configurações e retenção do ambiente.

[Voltar ao README principal](../../README.md)

