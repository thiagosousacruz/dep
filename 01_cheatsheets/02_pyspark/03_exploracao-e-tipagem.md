# Exploração e Tipagem (PySpark)

## O que é

Antes de transformar dados, inspecione schema, amostras, estatísticas e valores inválidos. Casts explícitos estabilizam joins e escritas; conversões incompatíveis produzem nulos ou erros conforme o modo ANSI e a função usada.

## Inspeção rápida

```python
df.printSchema()                                  # árvore de tipos, inclusive structs e arrays
df.limit(20).show(truncate=False)
df.select("idade", "faturamento").describe().show()   # count, mean, stddev, min, max
df.select("idade").summary("count", "min", "25%", "50%", "75%", "max").show()
display(df)                                       # Databricks: grade interativa e perfil de dados
```

- `describe` e `summary` são ações: percorrem os dados. Em tabelas grandes, rode sobre uma amostra (`df.sample(0.01, seed=42)`).
- `df.dtypes` e `df.schema` permitem validar o schema por código.

## Casts explícitos

```python
from pyspark.sql import functions as F
from pyspark.sql import types as T

df_tipado = (
    df_origem
    .withColumn("id", F.col("id").cast(T.LongType()))
    .withColumn("vl_faturamento", F.col("faturamento").cast(T.DecimalType(18, 2)))
    .withColumn("is_alta_compra", F.col("faturamento") > 1500)   # expressão booleana
)

# Contar o que o cast perdeu (valor presente que virou NULL)
df_tipado.filter(F.col("faturamento").isNotNull() & F.col("vl_faturamento").isNull()).count()
```

- Com ANSI ligado (padrão no Spark 4.x e no serverless), `cast` de valor inválido gera erro. `F.try_to_number`, `F.try_to_timestamp` ou `expr("try_cast(x AS INT)")` devolvem `NULL`.
- Use `DecimalType` para dinheiro; `DoubleType` é aproximado.

## Datas e timezone

`current_timestamp()` segue o timezone da sessão (`spark.sql.session.timeZone`). Converta explicitamente quando a origem e a sessão estiverem em fusos diferentes.

```python
df_datas = (
    df_logs
    .withColumn("dt_nascimento", F.to_date("dt_nascimento_txt", "dd/MM/yyyy"))
    .withColumn("ts_evento_br", F.from_utc_timestamp("ts_evento_utc", "America/Sao_Paulo"))
    .withColumn("mes_ref", F.date_trunc("month", "ts_evento_utc"))
)
```

- Os padrões de data são os mesmos do Spark SQL: `MM` = mês, `mm` = minuto, `HH` = 0–23.
- Só aplique `from_utc_timestamp` se a coluna estiver de fato em UTC.

## Checklist

- [ ] O schema lido confere com o contrato esperado?
- [ ] Perdas por cast são contadas?
- [ ] Valores monetários usam `DecimalType`?
- [ ] O fuso da origem e o da sessão são conhecidos?
