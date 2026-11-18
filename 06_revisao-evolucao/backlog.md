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
- [x] Camada de ensino (2026-11): `03_trilhas/` + `trilhas.html`, template de lição, 3 lições (execução do Spark, grão e cardinalidade, window functions), link "Aprenda o conceito" nos cheatsheets e `desafio.html?id=`.
- [x] Plano de 12 meses ligado ao hub; navegação cruzada entre as páginas; [mapa de skills](mapa-de-skills.md).
- [x] Núcleo das trilhas completo (2026-11): 9 lições, exemplo em SQL e PySpark, semanas do plano de 12 semanas ligadas às lições; build valida links das páginas escritas à mão.
- [x] Respostas da checagem nas 9 trilhas (2026-11).
- [x] Papéis definidos (2026-11): o curso linear é o `../engenharia_dados` (Databricks); este hub é consulta e revisão. O formato "livro" foi testado e descartado por ficar confuso; as trilhas viram aprofundamento e, aos poucos, módulos do curso.

## Próximas melhorias

Roteiro para o hub cobrir o ciclo completo (aprender → consultar → praticar → aplicar). As lacunas por skill estão no [mapa de skills](mapa-de-skills.md).

- [ ] **Portar trilhas para o curso** (`../engenharia_dados`, módulos 9–12): PySpark, execução e performance (trilhas 05–06), cargas e CDC (08), SCD2 (09). Apagar cada trilha portada.
- [ ] **Cheatsheets de plataforma** (consulta para os módulos 13–16 do curso): Auto Loader e COPY INTO · Lakeflow Jobs · Unity Catalog · Bundles e CI/CD.
- [ ] **Validar no Databricks** os trechos das trilhas 07–09 que não rodam em Spark local (`MERGE`, `DESCRIBE HISTORY`, Auto Loader, `IDENTITY`).
- [ ] **Modeling no build:** incluir `03_modeling-e-analytics` 01–03 no `build_docs.py`, com desafios de SCD2 e fato/dimensão.
- [ ] **Novos cheatsheets:** testes de pipelines PySpark · orquestração e reprocessamento · Unity Catalog · Lakeflow/DLT · CI/CD com Asset Bundles.
- [ ] **Prática integradora:** `projetos/` com 3–4 casos guiados (medallion com SCD2, ingestão incremental com reprocessamento, diagnóstico de performance, code review) e desafios dos tipos "diagnóstico" e "design".
- [x] Desafio do Dia atemporal (2026-11): fila que só avança com "Concluí", filtro por tema do cheatsheet; sem semanas nem data.
- [ ] **Progresso leve:** marcar "acertei / revisar" no Desafio do Dia (só `localStorage`); temas marcados voltam com mais frequência.

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
