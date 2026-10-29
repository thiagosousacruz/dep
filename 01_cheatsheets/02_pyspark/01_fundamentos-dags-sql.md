# Fundamentos: Lazy Evaluation, DAGs e Spark SQL (PySpark)

## O que é

O Spark não executa cada linha de código imediatamente. Transformações montam um plano; ações disparam a execução distribuída desse plano. DataFrame API e SQL compartilham o mesmo otimizador (Catalyst), então você pode alternar entre os dois.

## Transformações e ações

Transformações (`filter`, `select`, `withColumn`, `join`) são **lazy**: só descrevem um novo DataFrame. Ações (`count`, `show`, `collect`, `write`) executam o plano.

```python
from pyspark.sql import functions as F

df_filtrado = (
    df_origem
    .filter(F.col("nome").isNotNull())
    .withColumn("idade_ajustada", F.col("idade") + 1)
)  # nada foi lido ainda

df_filtrado.count()                                  # ação: executa o plano
df_filtrado.show(10)                                 # ação: executa de novo (sem cache)
df_filtrado.write.mode("overwrite").saveAsTable("silver.pessoas")
```

- Cada ação reexecuta o plano desde a origem, a menos que haja cache. Evite `count()` de depuração em pipelines de produção.
- `collect()` traz todos os dados para o driver: use apenas em resultados pequenos.
- Narrow transformations (`filter`, `select`) não exigem shuffle; wide transformations (`groupBy`, `join`, `orderBy`) redistribuem dados entre executores e criam novos estágios.

## DataFrame API vs RDD

RDDs oferecem controle de baixo nível, mas não expõem ao Catalyst a estrutura dos dados. Para transformações tabulares, a DataFrame API permite poda de colunas, pushdown de filtros e escolha de estratégia de join.

```python
df_vendas = spark.read.table("bronze.vendas")
df_fechadas = df_vendas.filter(F.col("status") == "FECHADO")
df_fechadas.explain("formatted")   # mostra o plano físico
```

- No Spark Connect (usado pela computação serverless e pelo modo compartilhado do Unity Catalog), a API de RDD e `sparkContext` não estão disponíveis.

## Spark SQL e temp views

```python
df_vendas.createOrReplaceTempView("vw_vendas")

df_resumo = spark.sql("""
    SELECT regiao, COUNT(*) AS transacoes, SUM(valor) AS receita
    FROM vw_vendas
    WHERE valor > 0
    GROUP BY regiao
""")

# Parâmetros nomeados em vez de f-string (Spark 3.4+)
df_regiao = spark.sql(
    "SELECT * FROM vw_vendas WHERE regiao = :regiao",
    args={"regiao": "SUL"},
)
```

- Temp views valem para a `SparkSession` atual. Global temp views (`global_temp`) valem para a aplicação Spark inteira, não para outros clusters, e não são suportadas em serverless.
- Montar SQL com f-string a partir de entrada externa abre espaço para SQL injection; prefira `args`.

## Imports e convenções

```python
from pyspark.sql import functions as F
from pyspark.sql import types as T
from pyspark.sql.window import Window
```

- Usar o namespace `F.` evita sombrear funções nativas do Python (`sum`, `max`, `round`, `filter`).

## Checklist

- [ ] As ações no código são intencionais (sem `count()`/`show()` de depuração)?
- [ ] `collect()`/`toPandas()` só recebem resultados pequenos?
- [ ] SQL dinâmico usa parâmetros em vez de concatenação?
- [ ] O código roda em Spark Connect se o destino for serverless?
