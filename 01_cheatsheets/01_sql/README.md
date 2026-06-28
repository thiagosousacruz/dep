# Cheatsheets SQL

Guias de referência rápida para SQL com foco em Databricks / Spark SQL e em tarefas comuns da rotina de engenharia de dados.

## Índice
- [Como usar esta pasta](#como-usar-esta-pasta)
- [Ordem sugerida de leitura](#ordem-sugerida-de-leitura)
- [Mapa dos cheatsheets](#mapa-dos-cheatsheets)
- [Como isso se conecta com practice](#como-isso-se-conecta-com-practice)
- [Quando ir para recipes](#quando-ir-para-recipes)

## Como usar esta pasta
Esta pasta funciona melhor como material de consulta rápida do que como leitura linear completa. A lógica ideal é:

1. Ler os arquivos iniciais para base operacional.
2. Ir para os tópicos analíticos conforme a necessidade.
3. Consultar os tópicos de Delta, quality e performance quando o problema já envolver Databricks, volumetria ou publicação de dados.

## Ordem sugerida de leitura

### Base operacional
1. [`01_sintaxe-basica.md`](01_sintaxe-basica.md)
2. [`02_tipos-e-formatos.md`](02_tipos-e-formatos.md)
3. [`03_sanitizacao-e-nomenclatura.md`](03_sanitizacao-e-nomenclatura.md)
4. [`04_nulos-e-condicionais.md`](04_nulos-e-condicionais.md)

### Transformação e análise
5. [`05_ctes.md`](05_ctes.md)
6. [`06_group-by-e-pivots.md`](06_group-by-e-pivots.md)
7. [`07_joins.md`](07_joins.md)
8. [`08_window-functions.md`](08_window-functions.md)

### Databricks / Lakehouse
9. [`09_json-structs.md`](09_json-structs.md)
10. [`10_delta-dml.md`](10_delta-dml.md)
11. [`11_data-quality-profiling.md`](11_data-quality-profiling.md)
12. [`12_performance-tuning.md`](12_performance-tuning.md)

## Mapa dos cheatsheets

### Fundamentos operacionais
- [`01_sintaxe-basica.md`](01_sintaxe-basica.md): ordem de execução, filtros, operadores e boas práticas de consulta básica.
- [`02_tipos-e-formatos.md`](02_tipos-e-formatos.md): `cast`, `try_cast`, `decimal`, parsing de datas e timezone.
- [`03_sanitizacao-e-nomenclatura.md`](03_sanitizacao-e-nomenclatura.md): limpeza de strings, alias, regex e padronização de nomes.
- [`04_nulos-e-condicionais.md`](04_nulos-e-condicionais.md): `coalesce`, `case`, impacto de nulos e flags de qualidade.

### Transformação analítica
- [`05_ctes.md`](05_ctes.md): modularização de queries e organização de lógica.
- [`06_group-by-e-pivots.md`](06_group-by-e-pivots.md): agregações, agrupamentos e estruturas de sumarização.
- [`07_joins.md`](07_joins.md): tipos de join, cardinalidade, exploding joins e hints.
- [`08_window-functions.md`](08_window-functions.md): ranking, acumulados, lag/lead e janelas analíticas.

### Databricks e escala
- [`09_json-structs.md`](09_json-structs.md): parsing de JSON, arrays, structs e flatten.
- [`10_delta-dml.md`](10_delta-dml.md): `merge`, time travel, `vacuum`, `optimize` e operações Delta.
- [`11_data-quality-profiling.md`](11_data-quality-profiling.md): checks rápidos de sanidade antes de publicar dados.
- [`12_performance-tuning.md`](12_performance-tuning.md): leitura de plano, pushdown, spill, reparticionamento e tuning.

## Como isso se conecta com practice
Os cheatsheets de SQL funcionam como material de apoio para a camada prática em [`../../practice/`](../../practice).

Use esta pasta para:
- revisar conceitos antes de resolver um exercício
- consultar sintaxe e padrões durante a resolução
- apoiar revisões técnicas sem duplicar teoria no módulo prático

Para praticar de fato:
- exercícios: [`../../practice/exercises/`](../../practice/exercises)
- soluções: [`../../practice/solutions/sql/`](../../practice/solutions/sql)
- workflow: [`../../practice/WORKFLOW.md`](../../practice/WORKFLOW.md)

## Quando ir para recipes
Se você já sabe o problema que quer resolver e quer um exemplo pronto para adaptar, vá para [`../../02_recipes/sql/`](../../02_recipes/sql).

Casos comuns:
- tratar nulos
- converter tipos
- deduplicar registros
- diagnosticar exploding joins
- comparar origem e destino
