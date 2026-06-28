# Data Engineering Playbook

Base pessoal e evolutiva de consulta rapida para SQL, PySpark e engenharia de dados, com foco em Databricks/Spark, problemas reais do dia a dia e evolucao pratica continua.

## Indice
- [Objetivo](#objetivo)
- [Como navegar](#como-navegar)
- [Estrutura do repositorio](#estrutura-do-repositorio)
- [Trilhas rapidas](#trilhas-rapidas)
- [Pastas principais](#pastas-principais)
- [Evolucao da base](#evolucao-da-base)

## Objetivo
O objetivo deste repositorio e transformar conhecimento tecnico disperso em uma base confiavel, pratica e facil de consultar. A ideia e reduzir retrabalho, acelerar resolucao de problemas recorrentes e manter uma trilha continua de aprendizado aplicada ao contexto real de engenharia de dados.

## Como navegar
Se voce estiver usando o repositorio pelo GitHub, a navegacao mais util costuma ser:

1. Comecar pelos cheatsheets de SQL ou PySpark.
2. Usar `04_templates/` para manter consistencia na documentacao.
3. Usar `06_revisao-evolucao/` para enxergar o que ainda falta melhorar na base.

## Estrutura do repositorio
O repositorio foi organizado como um pipeline de refinamento de conhecimento focado em referencias rapidas:

- [`01_cheatsheets/`](01_cheatsheets): base tecnica reutilizavel, com foco em referencia rapida.
- [`04_templates/`](04_templates): templates para manter consistencia na documentacao.
- [`06_revisao-evolucao/`](06_revisao-evolucao): backlog, avaliacoes e pontos de melhoria do playbook.

## Trilhas rapidas

### SQL (01_sql)
- Visao geral da area: [`01_cheatsheets/01_sql/README.md`](01_cheatsheets/01_sql/README.md)
- Cheatsheets SQL: [`01_cheatsheets/01_sql/`](01_cheatsheets/01_sql)

### PySpark (02_pyspark)
- Visao geral da area: [`01_cheatsheets/02_pyspark/README.md`](01_cheatsheets/02_pyspark/README.md)
- Cheatsheets PySpark: [`01_cheatsheets/02_pyspark/`](01_cheatsheets/02_pyspark)

### Modeling e Analytics (03_modeling-e-analytics)
- Visao geral da area: [`01_cheatsheets/03_modeling-e-analytics/README.md`](01_cheatsheets/03_modeling-e-analytics/README.md)
- Cheatsheets Analiticos: [`01_cheatsheets/03_modeling-e-analytics/`](01_cheatsheets/03_modeling-e-analytics)

### Revisao e evolucao
- Backlog atual: [`06_revisao-evolucao/backlog.md`](06_revisao-evolucao/backlog.md)
- Avaliacao da cobertura SQL: [`06_revisao-evolucao/sql-cobertura-avaliacao.md`](06_revisao-evolucao/sql-cobertura-avaliacao.md)
- Avaliacao da cobertura PySpark: [`06_revisao-evolucao/pyspark-cobertura-avaliacao.md`](06_revisao-evolucao/pyspark-cobertura-avaliacao.md)
- Avaliacao de Modeling e Analytics: [`06_revisao-evolucao/modeling-analytics-cobertura-avaliacao.md`](06_revisao-evolucao/modeling-analytics-cobertura-avaliacao.md)

## Pastas principais

### `01_cheatsheets`
Area de consulta rapida. Hoje concentra principalmente:

- **`01_sql:`** Sintaxe, tipos, sanitizacao, nulos, joins, windows, JSON, Delta, data quality e performance.
- **`02_pyspark:`** Fundamentos do Spark, IO, DataFrame API, joins, windows, JSON, Delta, quality e arquitetura.
- **`03_modeling-e-analytics:`** Modelagem dimensional, schemas estrela, Slowly Changing Dimensions, semantic layer e design de consumo em BI.

### `04_templates`
Templates de padronizacao para documentacao e notebooks.

### `06_revisao-evolucao`
Backlog atual e mapas de avaliacao de cobertura dos assuntos, auxiliando a focar os conteudos que devem ser produzidos e estruturados.

## Evolucao da base
O repositorio e intencionalmente vivo. Os ajustes e lacunas identificadas ficam concentrados em [`06_revisao-evolucao/`](06_revisao-evolucao).
