# Data Quality Operacional (PySpark)

## O que é

Checagens executadas no próprio pipeline, antes de publicar Silver ou Gold: unicidade do grão, nulos em campos críticos, perda de linhas em joins e variação de volume. A regra precisa definir o limite aceitável e a ação (alertar, isolar ou falhar).

## Unicidade do grão

```python
from pyspark.sql import functions as F

resumo = df_final.agg(
    F.count("*").alias("linhas"),
    F.count_distinct("id_transacao").alias("chaves"),
).first()

if resumo["linhas"] != resumo["chaves"]:
    raise ValueError(
        f"Grão violado: {resumo['linhas']} linhas para {resumo['chaves']} chaves distintas"
    )
```

- Faça as métricas em um único `agg`: cada ação separada relê os dados.
- `print` não interrompe um job; para bloquear a publicação, levante exceção.

## Percentual de nulos por coluna

```python
def percentual_nulos(df, colunas):
    linha = df.select([
        (F.avg(F.col(c).isNull().cast("int")) * 100).alias(c) for c in colunas
    ]).first()
    return linha.asDict()

nulos = percentual_nulos(df_clientes, ["telefone", "email", "cpf"])
violacoes = {c: p for c, p in nulos.items() if p > 25.0}
if violacoes:
    print(f"Alerta de qualidade: nulos acima de 25% em {violacoes}")
```

- O limite (25% acima) é exemplo: defina-o com o consumidor do dado.

## Perda de linhas em joins

Compare a origem com o resultado e isole as linhas sem correspondência, em vez de só contar.

```python
sem_dimensao = df_vendas.join(df_produtos, "id_produto", "left_anti")
qtd_orfas = sem_dimensao.count()
total = df_vendas.count()

if total and qtd_orfas / total > 0.01:
    sem_dimensao.write.mode("append").saveAsTable("main.quarentena.vendas_sem_produto")
    raise ValueError(f"{qtd_orfas} de {total} vendas sem produto correspondente")
```

- Para um `inner join`, a diferença de contagem também pode vir de duplicidade do lado direito (que **aumenta** linhas); verifique as duas direções.

## Frameworks e expectativas declarativas

Para regras recorrentes, prefira declarar em vez de codificar `if` a cada pipeline:

- **Lakeflow Declarative Pipelines (DLT):** `@dlt.expect`, `@dlt.expect_or_drop`, `@dlt.expect_or_fail`, com métricas por regra.
- **Restrições Delta:** `CHECK` e `NOT NULL` na tabela (ver [Data quality em SQL](../01_sql/11_data-quality-profiling.md)).
- Bibliotecas como DQX (Databricks Labs) e Great Expectations, quando o projeto as adota.

## Checklist

- [ ] Cada regra tem limite e ação definidos?
- [ ] Violações bloqueiam a publicação quando deveriam?
- [ ] Linhas rejeitadas vão para quarentena com contexto?
- [ ] As métricas são calculadas com o mínimo de ações?
