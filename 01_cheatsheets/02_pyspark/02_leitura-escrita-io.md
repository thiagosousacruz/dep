# Leitura e Escrita de Dados (PySpark I/O)

## O que e
Processos primários de interacao (`spark.read` e `DataFrame.write`) sobre fontes fisicas no HD/Storage. Determinam o sucesso da ingestao, mitigando o desperdicio de conexoes ociosas em banco de dados operacionais ou controlando partições otimizadas do Databricks no Data Lake.

## Nivel Junior/Pleno: Leitura Analitica Variada
A definicao explícita do schema e preceito base para economizar verificações profundas (`Pass-scanning`) onde o spark vasculha tudo pra inferir os tipos as cruas.

```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

schema_fixo = StructType([
    StructField("id", IntegerType(), False),
    StructField("cidade", StringType(), True)
])

# LEITURA CONTROLADA TABULAR (CSVS)
df_csv = spark.read \\
    .schema(schema_fixo) \\
    .option("header", "true") \\
    .option("delimiter", ";") \\
    .csv("/mnt/bronze/lotes/*.csv") # Suporta pathings GLOB nativamente

# LEITURAS NATIVAS DE COMPRESSAO APROPRIADA (Lakes)
df_parquet = spark.read.parquet("/mnt/bronze/")
df_delta = spark.read.format("delta").load("/mnt/silver/")

# LEITURAS JSON PAYLOADS (Quebras Esteticas)
# O padrao comum de leitura le json-lines (Por Row unica). Se o payload traz o JSON em bloco identado/multilinhas esparso esteticamente, defina 'multiline':
df_json = spark.read \\
    .option("multiline", "true") \\
    .json("/mnt/bronze/payloads/*.json")
```

## Nivel Pleno: Leitura JDBC Paralelizada
Diferente de um `read.parquet`, consultar fontes on-premise (Sistemas Legados, Oracle, SQL Server) seca restringe um canal de coneçao 1:1, focando 100% da query massiva num node Worker solteiro que falhará o timeout (OOM/Table Locking).

```python
# Distribuimos e paralelizamos a query no DB: O Spark dividirá o escopo base (1 a 5 Milhoes do alvo column id_venda) num array partitivo enviando 10 requestes simultaneamente pra encher a malha relacional.
df_erp = spark.read.jdbc(
    url="jdbc:sqlserver://servidor.database.windows.net:1433;database=DB",
    table="vendas.faturamento",
    column="id_venda",      
    lowerBound=1,
    upperBound=5000000,
    numPartitions=10,       
    properties={"user": "...", "password": "..."}
)
```

## Nivel Senior: Gravacao particionada estrutural
Como gravar em conformidades HDFS `(pathing fisico= /../ano=2024/mes=10/part-004.parquet)`.

```python
df_resultado.write \\
    .format("delta") \\
    .mode("overwrite") \\
    .partitionBy("ano", "mes") \\
    .save("/mnt/gold/agregado_mensal")
    
# ALERTA DE ARQUITETURA CRITICA: "The Small File Problem"
# Jamais gere um particionamento fisico massudo baseado em colunas de alta cardinalidade(ex `partitionBy('id_carrinho_compra')`)! O Spark fisicamente criará pastas microscopicas gerando 2 MIHLÕES DE ARQUIVOS PARQUET de 14 Kb limitando transacoes no File System e engargalando disco por excesso logístico! Só Particiione em blocos que segurarão lotes grandes +150MB.
```
