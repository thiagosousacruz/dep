# JSON, Structs e Schemas (PySpark)

## O que é

Dados semiestruturados exigem distinguir **texto JSON** (`StringType`) de colunas já tipadas (`StructType`, `ArrayType`, `MapType`). Um schema explícito torna o contrato observável; registros incompatíveis ainda precisam ser medidos e tratados.

## Acessar campos de structs e de texto JSON

```python
from pyspark.sql import functions as F

# Coluna struct já tipada: notação de ponto
df_proto = df_ingestao.select(
    "id_registro",
    F.col("metadata.rede.versao_tls").alias("versao_tls"),
)

# Coluna string com JSON: extração por caminho
df_ids = df_bronze.withColumn(
    "id_core",
    F.get_json_object("payload_txt", "$.root.identificadores[0].idCore"),
)
```

- `get_json_object` reprocessa o texto a cada chamada. Para vários campos, converta uma vez com `from_json`.

## Explode de arrays

`explode` gera uma linha por elemento e muda o grão do DataFrame.

```python
df_tags = (
    df_receitas
    .withColumn("tags", F.split("tags_texto", ","))
    .withColumn("tag", F.explode_outer("tags"))   # mantém linhas com array vazio/nulo
)

# Transformar sem explodir: funções de ordem superior
df_itens = df_pedidos.withColumns({
    "itens_caros": F.filter("itens", lambda x: x["valor"] > 25),
    "total":       F.aggregate(
        "itens",
        F.lit(0).cast("decimal(12,2)"),
        lambda acc, x: (acc + x["valor"]).cast("decimal(12,2)"),   # acumulador mantém o tipo inicial
    ),
})
```

- `explode` descarta linhas com array vazio ou nulo; `explode_outer` as preserva com `null`.
- `posexplode` também devolve a posição do elemento.

## Schema explícito na leitura e from_json

```python
from pyspark.sql import types as T

schema_vendas = T.StructType([
    T.StructField("id_venda", T.StringType(), nullable=False),
    T.StructField("valor", T.DecimalType(12, 2), nullable=True),
    T.StructField("_corrupt", T.StringType(), nullable=True),
])

df_vendas = (
    spark.read
    .schema(schema_vendas)
    .option("columnNameOfCorruptRecord", "_corrupt")
    .json("/Volumes/main/bronze/landing/vendas/")
)
df_vendas.filter(F.col("_corrupt").isNotNull()).count()   # registros que não seguiram o schema

# Texto JSON em uma coluna → struct tipada
schema_evento = "STRUCT<nome: STRING, idade: INT, ativo: BOOLEAN>"   # DDL também é aceito
df_evento = df_bronze.withColumn("evento", F.from_json("payload_txt", schema_evento))
```

- `nullable=False` no schema de leitura **não** rejeita nulos em arquivos: valide depois.
- `F.schema_of_json` ajuda a sugerir um schema a partir de um exemplo; fixe o resultado no código em vez de inferir em produção.

## Colunas obrigatórias ausentes

Quando cargas diárias podem omitir campos, adicione os ausentes com tipo explícito para manter o schema estável.

```python
colunas_obrigatorias = {"id": "bigint", "nome": "string", "campo_opcional": "string"}

df_estavel = df_evento.withColumns({
    nome: F.lit(None).cast(tipo)
    for nome, tipo in colunas_obrigatorias.items()
    if nome not in df_evento.columns
})
```

- `F.lit(None)` sem `cast` cria uma coluna `void`, que falha ao gravar em Delta.

## VARIANT

Para JSON de estrutura instável, o tipo `VARIANT` (Databricks Runtime 15.3+) armazena o documento de forma binária e consulta caminhos sem schema fixo: `F.parse_json("payload_txt")` e `F.try_variant_get(col, "$.campo", "int")`, disponíveis na API Python a partir do Spark 4.0 (ver [JSON e structs em SQL](../01_sql/09_json-structs.md)).

## Checklist

- [ ] Está claro quais colunas são texto JSON e quais são structs?
- [ ] Registros corrompidos são capturados e contados?
- [ ] Colunas adicionadas por código têm tipo explícito?
- [ ] O novo grão após `explode` está documentado?
