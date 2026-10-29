# Agrupamentos, Agregações e Pivots (PySpark)

## O que é

`groupBy().agg()` resume linhas em métricas por grupo. `pivot` gira valores de uma coluna em colunas; `unpivot` faz o inverso. Calcular todas as métricas em um único `agg` evita várias passadas sobre os dados.

## Várias agregações em uma passada

```python
from pyspark.sql import functions as F

df_resumo = (
    df_fatos
    .groupBy("ano_fiscal", "uf")
    .agg(
        F.count("id_transacao").alias("qtd_vendas"),
        F.round(F.avg("lucro"), 2).alias("lucro_medio"),
        F.count_if(F.col("status") == "ERRO").alias("qtd_erros"),          # Spark 3.5+
        F.sum(F.when(F.col("canal") == "LOJA", F.col("valor"))).alias("valor_loja"),
        F.approx_count_distinct("id_cliente", rsd=0.02).alias("clientes_aprox"),
    )
)

# Agregação sem agrupamento: uma linha com o total
total = df_fatos.agg(F.sum("valor").alias("total")).first()["total"]
```

- `approx_count_distinct` usa HyperLogLog++ com erro relativo padrão de **5%** (`rsd=0.05`). Valores menores de `rsd` aumentam precisão e memória. `F.count_distinct` é exato, porém mais caro em alta cardinalidade.
- Use `F.sum`, `F.max`, `F.round` com o namespace: importar `sum`/`round` diretamente sombreia as funções do Python.

## Pivot

```python
df_pivotado = (
    df_vendas
    .groupBy("categoria")
    .pivot("ano", [2023, 2024, 2025])   # lista explícita
    .agg(F.sum("receita"))
)
# | categoria | 2023 | 2024 | 2025 |
```

- Sem a lista de valores, o Spark executa uma consulta extra para descobri-los, e o número de colunas passa a depender dos dados.

## Unpivot (melt)

```python
df_longo = df_planilha.unpivot(          # Spark 3.4+ (alias: melt)
    ids=["regiao"],
    values=["receita_jan", "receita_fev", "receita_mar"],
    variableColumnName="mes",
    valueColumnName="receita",
)
```

- As colunas em `values` precisam ter tipos compatíveis.

## Subtotais: rollup e cube

```python
df_subtotais = (
    df_vendas
    .rollup("pais", "regiao")
    .agg(F.sum("valor").alias("valor"), F.grouping_id().alias("nivel"))
)
```

- `rollup` gera (pais, regiao), (pais) e o total; `cube` gera todas as combinações. `grouping_id` distingue subtotal de `null` real.

## Checklist

- [ ] Todas as métricas do grupo estão em um único `agg`?
- [ ] O erro aceitável de contagens aproximadas foi definido?
- [ ] O `pivot` recebe a lista de valores?
- [ ] O grão do resultado está documentado?
