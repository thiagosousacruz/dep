# Leitura e Escrita de Dados (PySpark I/O)

## O que é

`spark.read` e `DataFrame.write` conectam o pipeline a arquivos, tabelas e bancos externos. As opções escolhidas definem custo de leitura, paralelismo, tratamento de registros inválidos e layout físico do resultado.

## Arquivos com schema explícito

Sem schema, o Spark precisa inferir tipos (passada extra sobre os dados e tipos instáveis entre cargas). Declare o schema em ingestões recorrentes.

```python
from pyspark.sql import types as T

schema_lote = T.StructType([
    T.StructField("id", T.IntegerType(), False),
    T.StructField("cidade", T.StringType(), True),
])

df_csv = (
    spark.read
    .schema(schema_lote)
    .option("header", "true")
    .option("sep", ";")
    .option("mode", "PERMISSIVE")                     # inválidos viram NULL
    .option("columnNameOfCorruptRecord", "_corrupt")  # guarda a linha original
    .csv("/Volumes/main/bronze/landing/lotes/*.csv")
)

df_json = spark.read.option("multiLine", "true").json("/Volumes/main/bronze/landing/payloads/")
df_parquet = spark.read.parquet("/Volumes/main/bronze/landing/parquet/")
```

- `mode`: `PERMISSIVE` (padrão), `DROPMALFORMED` (descarta) ou `FAILFAST` (falha no primeiro inválido).
- Para a coluna `_corrupt` ser preenchida, ela precisa estar no schema.
- Com Unity Catalog, arquivos ficam em **Volumes** (`/Volumes/<catálogo>/<schema>/<volume>/`); mounts em `/mnt` são legado.

## Tabelas

```python
df = spark.read.table("main.silver.clientes")

(
    df_resultado.write
    .mode("overwrite")              # append | overwrite | error | ignore
    .saveAsTable("main.gold.agregado_mensal")
)
```

- Em Databricks, `saveAsTable` grava Delta por padrão e registra a tabela no catálogo.
- Para sobrescrever só parte da tabela, use `.option("replaceWhere", "mes = '2025-10'")` em vez de `overwrite` total.

## JDBC paralelizado

Sem particionamento, uma leitura JDBC usa uma única conexão. Com `column`, `lowerBound`, `upperBound` e `numPartitions`, o Spark divide a consulta em faixas.

```python
df_erp = spark.read.jdbc(
    url="jdbc:sqlserver://servidor.database.windows.net:1433;database=DB",
    table="vendas.faturamento",
    column="id_venda",
    lowerBound=1,
    upperBound=5_000_000,
    numPartitions=10,
    properties={
        "user": dbutils.secrets.get("erp", "usuario"),
        "password": dbutils.secrets.get("erp", "senha"),
    },
)
```

- `lowerBound` e `upperBound` **não filtram** dados: só definem o tamanho das faixas. Linhas fora delas vão para a primeira e a última partição.
- `numPartitions` é o número de conexões simultâneas na origem; combine com o dono do banco.
- Escolha uma coluna numérica/data bem distribuída; uma coluna com skew concentra o trabalho.
- Alternativa no Databricks: Lakehouse Federation consulta a origem como catálogo, sem código JDBC.

## Particionamento físico e arquivos pequenos

```python
(
    df_resultado.write
    .mode("overwrite")
    .partitionBy("ano", "mes")
    .saveAsTable("main.gold.vendas_mensal")
)
```

- Particionar por coluna de alta cardinalidade (ex.: `id_cliente`) gera milhares de diretórios e arquivos pequenos, degradando leitura e manutenção.
- O Databricks recomenda não particionar tabelas pequenas (orientação oficial: menos de ~1 TB) e, em tabelas novas, preferir **liquid clustering** (ver [Delta Lake API](10_delta-lake-api.md)).

## Checklist

- [ ] Ingestões recorrentes têm schema declarado?
- [ ] Registros inválidos são capturados e medidos?
- [ ] Credenciais vêm de secrets, nunca do código?
- [ ] O layout físico (partição ou clustering) foi escolhido pelos filtros reais?
