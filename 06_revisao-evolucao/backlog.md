# Backlog de Revisão e Evolução

O núcleo ativo cobre SQL e PySpark. Modeling permanece complementar; streaming e recipes estão fora do ciclo atual. A prática diária é feita pelo Desafio do Dia, que cobre apenas o conteúdo dos cheatsheets.

## Concluído

- [x] Declarar Markdown como fonte de verdade e HTML como artefato gerado.
- [x] Corrigir links para áreas inexistentes ou renomeadas.
- [x] Documentar Modeling como conteúdo complementar fora do build.
- [x] Revisar joins, windows, Catalyst, spill, repartition/coalesce, skew, Pandas UDF e Delta.
- [x] Remover recomendações absolutas e números de performance sem evidência.
- [x] Tornar o build independente do diretório de execução.
- [x] Validar entradas, placeholders, links internos e contagem de seções.
- [x] Preservar a estrutura semântica `pre > code` no HTML.
- [x] Documentar dependências e comando de geração.
- [x] Revisão técnica e editorial completa (2026-10): ver [revisao-editorial-2026-10.md](revisao-editorial-2026-10.md).
- [x] Correções de SQL de 2026-10-28: `CACHE VIEW`, CTE × plano, `approx_count_distinct` 5%, ordem de execução, `IFF`.

## Próximas melhorias

- [ ] Revisão periódica por versão do runtime usando [o checklist](../04_templates/checklist-revisao-editorial.md).
- [ ] Automatizar o build e o verificador de links em CI caso o projeto seja publicado.
- [ ] Expandir exemplos somente a partir de casos reais validados.

## Lacunas identificadas (aguardando decisão de escopo)

Prioridade: **A** = esperado no tema e de uso frequente · **M** = útil · **B** = avançado ou nichado.

### SQL

- [ ] **A** `08_window-functions.md`: `RANGE BETWEEN INTERVAL` para janelas por tempo, `lead`, `first_value`/`last_value` com `IGNORE NULLS`, `ntile`, `percent_rank`.
- [ ] **A** `10_delta-dml.md`: `DESCRIBE HISTORY`, `MERGE ... WHEN NOT MATCHED BY SOURCE` (delete/soft delete), `MERGE WITH SCHEMA EVOLUTION`, `INSERT REPLACE WHERE`, colunas `IDENTITY`, Change Data Feed.
- [ ] **A** `07_joins.md`: joins por intervalo (data entre vigências de SCD2) e `NOT EXISTS` vs `LEFT ANTI JOIN`.
- [ ] **M** `02_tipos-e-formatos.md`: `make_date`, `months_between`, `last_day`, `TIMESTAMP_NTZ` vs `TIMESTAMP`.
- [ ] **M** `12_performance-tuning.md`: Photon, `ANALYZE TABLE ... COMPUTE STATISTICS`, data skipping, Query Profile do DBSQL.
- [ ] **M** Novo tópico: Unity Catalog essencial (namespace de 3 níveis, `GRANT`, views dinâmicas, linhagem).
- [ ] **B** `03_sanitizacao`: funções de similaridade (`levenshtein`, `soundex`) e normalização Unicode.
- [ ] **B** SQL scripting (`BEGIN ... END`, variáveis `DECLARE`) e funções SQL definidas pelo usuário.

### PySpark

- [ ] **A** `02_leitura-escrita-io.md`: Auto Loader (`cloudFiles`) para ingestão incremental de arquivos, mesmo fora de streaming contínuo (`trigger(availableNow=True)`).
- [ ] **A** `10_delta-lake-api.md`: `whenNotMatchedBySourceDelete`, `history()`, leitura de Change Data Feed, `replaceWhere`.
- [ ] **A** `13_performance-e-arquitetura.md`: `cache`/`persist` (e a limitação no serverless), `spark.sql.shuffle.partitions` vs AQE.
- [ ] **M** `08_window-functions.md`: `rangeBetween` com timestamp convertido em segundos, `first`/`last` com `ignorenulls`.
- [ ] **M** `13_performance-e-arquitetura.md`: `pyspark.testing.assertDataFrameEqual` (Spark 3.5+).
- [ ] **M** Novo tópico: Lakeflow Declarative Pipelines (DLT) e expectations, ligado ao 12 e ao 14.
- [ ] **B** Python Data Source API e UDTFs (Spark 4.x).
- [ ] **B** `14_medallion-architecture.md`: sem acentuação e sem exemplos de código; avaliar exemplo mínimo por camada.
