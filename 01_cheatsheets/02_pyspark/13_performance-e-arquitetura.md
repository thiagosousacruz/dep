# Performance, Arquitetura e Testes em PySpark

> **Aprenda o conceito:** trilhas [Como o Spark executa seu código](../../03_trilhas/05_como-o-spark-executa.md) · [Diagnóstico de performance](../../03_trilhas/06_diagnostico-de-performance.md) — modelo mental, exemplo para prever e erros comuns.

## Diagnóstico antes da otimização

Use `explain("formatted")`, Spark UI e métricas do job para identificar leitura, exchanges, sorts, skew, spill e tarefas lentas. Compare resultado e custo antes e depois de cada mudança.

```python
df_resultado.explain("formatted")
```

## AQE e partições

AQE pode ajustar o plano com estatísticas de runtime, coalescer partições pós-shuffle e tratar alguns skew joins. Em runtimes gerenciados, confira os defaults antes de sobrescrever configurações.

```python
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
```

- `repartition(n, *cols)` executa redistribuição e pode aumentar ou reduzir partições. Use quando precisa balancear dados, particionar por chave ou elevar paralelismo.
- `coalesce(n)` costuma reduzir partições sem shuffle completo. É útil após filtros fortes, mas pode criar partições desbalanceadas.
- Não existe um número universal de partições. Considere volume, tamanho das tarefas, núcleos disponíveis e escrita final.

```python
df_por_cliente = df.repartition(200, "cliente_id")
df_saida = df_filtrado.coalesce(20)
```

## Skew e salting

Meça frequência das chaves e duração das tarefas. Primeiro avalie filtros, AQE, broadcast do lado pequeno e revisão da chave. Salting replica ou transforma dados e deve ser reservado para skew comprovado.

```python
from pyspark.sql import functions as F

df.groupBy("chave").count().orderBy(F.desc("count")).show(20, truncate=False)
```

## Funções nativas, Python UDF e Pandas UDF

Prefira expressões nativas do Spark: elas são visíveis ao otimizador e evitam fronteiras Python desnecessárias. Pandas UDF processa lotes via Arrow e pode ser melhor que uma Python UDF linha a linha, mas ainda tem serialização, memória e restrições de tipos. Use-a apenas quando não houver expressão nativa adequada e meça.

```python
from pyspark.sql import functions as F

df_classificado = df.withColumn(
    "classificacao",
    F.when(F.col("saldo") > 2_500_000, "VIP").otherwise("STANDARD"),
)
```

## Separação de responsabilidades

Mantenha transformação pura separada de leitura, escrita e configuração. Isso facilita testes e evita acoplar regra de negócio ao notebook.

```python
from pyspark.sql import functions as F

def aplicar_imposto(df):
    return df.withColumn("imposto", F.col("valor") * F.lit(0.17))
```

## Teste local

```python
def test_aplicar_imposto(spark):
    entrada = spark.createDataFrame([(100.0,)], ["valor"])
    resultado = aplicar_imposto(entrada).first()
    assert resultado.imposto == 17.0
```

Sessões Spark locais são integrações leves, não mocks. Para comparações decimais, use tipos decimais ou tolerância apropriada.

## Checklist

- [ ] O gargalo foi observado no plano ou na UI?
- [ ] Funções nativas foram consideradas antes de UDFs?
- [ ] Repartition/coalesce têm objetivo e métrica definidos?
- [ ] Transformações são testáveis sem I/O externo?
- [ ] A otimização preservou o resultado?

