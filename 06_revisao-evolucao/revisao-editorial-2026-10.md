# Revisão Técnica e Editorial — Outubro/2026

Critérios: [`04_templates/checklist-revisao-editorial.md`](../04_templates/checklist-revisao-editorial.md). Runtime-alvo: Databricks SQL / Databricks Runtime atuais (Spark 4.x).

**Como foi verificado.** Os blocos Python foram conferidos com `ast.parse`. As funções e a sintaxe citadas foram executadas em PySpark 4.1.2 local. Recursos exclusivos do Databricks (`iff`, `QUALIFY`, operador `:` em string, `CACHE TABLE` em serverless) foram conferidos na documentação oficial.

Severidade: **E** erro · **D** defasado · **Di** didática · **T** tom · **L** lacuna (vai para o backlog).

## Problema transversal

| Sev. | Achado | Correção |
|---|---|---|
| E | Os blocos PySpark usavam `\\` (duas barras) para quebrar linha, com comentários entre os métodos encadeados. Copiado, o código dava erro de sintaxe. | Encadeamento entre parênteses em todos os arquivos. 0 erros no `ast.parse`. |
| T | O tom variava muito entre arquivos: caixa alta, gírias e exageros ("velocidade assombrosa", "te acorda às 3 da manhã"). | Os arquivos no estilo antigo foram reescritos no padrão de 07/08/10/12. |
| D | Caminhos `/mnt/...` em todos os exemplos de I/O. | Trocados por Volumes do Unity Catalog e `read.table`. |

## SQL

| Arquivo | Sev. | Achado | Correção |
|---|---|---|---|
| 01 | E | A ordem de execução omitia janelas, `QUALIFY`, `DISTINCT` e `LIMIT`. | Ordem lógica completa. `QUALIFY` marcado como exclusivo do Databricks. |
| 01 | Di | Faltava a armadilha `NOT IN` com `NULL` (verificado: retorna 0 linhas). | Seção com a alternativa `NOT EXISTS`. |
| 01 | Di | Faltava a armadilha `BETWEEN` com `DATE` em coluna `TIMESTAMP`, além de `LIKE`/`ILIKE` e `EXCEPT ALL`. | Incluídos. |
| 02 | D | Não mencionava o modo ANSI padrão (o `CAST` inválido gera erro). | Seção "CAST, TRY_CAST e modo ANSI". |
| 03 | E | `RENAME COLUMN` em Delta exige column mapping, e isso não era dito. | Pré-requisito, impactos e link oficial. |
| 03 | E | Dizia "core do Spark C++". O Spark roda na JVM; o motor C++ é o Photon. | Removido. |
| 04 | E | `IFF` não existe no Spark open source (verificado). | `CASE WHEN`, com nota de portabilidade. |
| 04 | D | Divisão por zero gera erro com ANSI; faltava `try_divide`. | Incluído. |
| 05 | E | `CACHE VIEW` não existe. | `CACHE TABLE`, com a limitação do serverless e a alternativa de tabela intermediária. |
| 05 | E | Afirmava que a CTE é sempre relida N vezes, contradizendo o 12. | Alinhado: depende do plano (`ReusedExchange`). |
| 05 | E | O exemplo de `UNION` usava aliases inexistentes. | Exemplo refeito. |
| 05 | E | Dizia que a temp view dura "até o fim do cluster"; ela é da sessão. | Corrigido. Global temp views não funcionam em serverless. |
| 05 | L→ | Faltava `WITH RECURSIVE` (DBR 17.0+). | Incluído, por ser o recurso nativo do tema. |
| 06 | E | `approx_count_distinct` com "2% de erro"; o padrão é 5%. | Corrigido, com o parâmetro de precisão. |
| 06 | Di | Faltavam `grouping()` / `grouping_id()` para distinguir subtotal, além de `GROUPING SETS` e `GROUP BY ALL`. | Incluídos. |
| 09 | E | `LATERAL VIEW` sem alias de tabela. | Corrigido. Adicionados `posexplode`, `explode_outer` e funções de ordem superior. |
| 09 | D | Faltava o tipo `VARIANT` (DBR 15.3+). | Seção curta com link oficial. |
| 10 | D | `ZORDER` era apresentado sem a recomendação atual. | Liquid clustering e predictive optimization. |
| 11 | Di | A checagem de grão usava `id_cliente` como exemplo de chave de pedido. | Chave coerente. Restrições `CHECK` e `NOT NULL` incluídas. |

## PySpark

| Arquivo | Sev. | Achado | Correção |
|---|---|---|---|
| 01 | E | Global temp view descrita como "cross-cluster". | Escopo da aplicação Spark e limitação do serverless. |
| 01 | D | Faltavam Spark Connect (sem RDD/`sparkContext` no serverless) e SQL parametrizado. | Incluídos. |
| 02 | E | Não dizia que `lowerBound` e `upperBound` do JDBC **não filtram** dados. | Incluído. |
| 02 | Di | "+150MB por partição" sem fonte. | Trocado pela orientação oficial e pelo liquid clustering. |
| 02 | Di | Faltava o tratamento de registros corrompidos (`mode`, `columnNameOfCorruptRecord`). | Incluído. |
| 03 | E | Dizia que o padrão de data `MM` "difere do SQL"; é o mesmo. | Corrigido. |
| 04 | E | `orderBy` seguido de `dropDuplicates` "mantém a primeira": não há essa garantia. | Janela com `row_number` e desempate. |
| 04 | E | Filtro misturava `&` e `|` sem agrupar. | Agrupamento explícito e regra de precedência. |
| 04 | D | Faltavam `withColumns` e `withColumnsRenamed`. | Incluídos. |
| 05 | D | Faltava `try_divide`; ANSI no Spark 4.x. | Incluídos. |
| 06 | E | "~2%" de erro no `approx_count_distinct`; o padrão é `rsd=0.05`. | Corrigido. |
| 06 | E | `from ... import sum, round` sombreava funções nativas do Python, e `col` não era importado. | Namespace `F.`. |
| 09 | E | `lit(None)` sem cast gera coluna `void`. | Cast explícito. |
| 09 | E | O `aggregate` com acumulador `DECIMAL` falha por tipo (verificado). | Cast do acumulador. |
| 11 | D | DBFS e mounts eram tratados como padrão. | Volumes e job parameters. Ressalva de que o `[REDACTED]` não é proteção completa. |
| 12 | Di | Os checks usavam `print` (não bloqueia o job) e várias ações. | `raise`, agregação única, quarentena com `left_anti` e expectativas declarativas. |

Sem alterações: SQL 07, 08, 12 e PySpark 07, 08, 13, 14 (já revisados na consolidação). Lacunas desses arquivos estão no backlog.

## Fontes

- [Limitações do serverless (CACHE TABLE, global temp views)](https://docs.databricks.com/aws/en/compute/serverless/limitations)
- [Delta column mapping](https://docs.databricks.com/aws/en/delta/column-mapping)
- [CTE e WITH RECURSIVE](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-qry-select-cte)
- [try_variant_get / VARIANT](https://docs.databricks.com/aws/en/sql/language-manual/functions/try_variant_get)
- [Liquid clustering](https://docs.databricks.com/aws/en/delta/clustering)
