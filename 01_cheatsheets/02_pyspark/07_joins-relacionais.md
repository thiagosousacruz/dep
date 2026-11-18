# Joins em PySpark

> **Aprenda o conceito:** trilha [Grão e cardinalidade](../../03_trilhas/02_grao-e-cardinalidade.md) — modelo mental, exemplo para prever e erros comuns.

## O que são

`DataFrame.join` combina DataFrames por nomes de colunas ou expressões. Em escala, avalie cardinalidade, volume de shuffle, distribuição das chaves e estratégia física.

## Chaves com o mesmo nome

Passar os nomes em `on` mantém uma única cópia dessas colunas no resultado. Isso resolve a ambiguidade de nomes, mas não remove linhas duplicadas nem altera a cardinalidade.

```python
df_resultado = df_vendas.join(
    df_lojas,
    on=["loja_id"],
    how="left",
)
```

Para nomes diferentes ou condições compostas, use aliases e projete explicitamente a saída.

```python
from pyspark.sql import functions as F

v = df_vendas.alias("v")
c = df_cambio.alias("c")

df_convertido = (
    v.join(
        c,
        (F.col("v.moeda") == F.col("c.codigo"))
        & (F.col("v.data_venda") == F.col("c.data_referencia")),
        "left",
    )
    .select("v.*", F.col("c.taxa").alias("taxa_cambio"))
)
```

## Semi e anti join

```python
df_com_acesso = df_clientes.join(df_acessos, "cliente_id", "left_semi")
df_sem_acesso = df_clientes.join(df_acessos, "cliente_id", "left_anti")
```

Essas estratégias filtram a esquerda sem transportar colunas da direita.

## Broadcast

`broadcast()` é apropriado quando o DataFrame transmitido cabe com folga na memória de cada executor. Estatísticas desatualizadas ou dados maiores que o esperado podem tornar a decisão pior que um shuffle join.

```python
from pyspark.sql.functions import broadcast

df_resultado = df_fato.join(
    broadcast(df_dimensao_pequena),
    on="produto_id",
    how="left",
)

df_resultado.explain("formatted")
```

## Cuidados

- Valide duplicidades por chave antes de assumir relação 1:1.
- Alinhe os tipos das chaves antes do join.
- Não use `dropDuplicates` para esconder cardinalidade inesperada.
- Compare contagens e métricas segundo o grão esperado.
- Para skew, meça a distribuição e avalie AQE antes de aplicar salting.

## Checklist

- [ ] O grão de cada DataFrame é conhecido?
- [ ] O tipo de join preserva as linhas pretendidas?
- [ ] A projeção evita colunas duplicadas ou desnecessárias?
- [ ] O plano confirma broadcast, sort-merge ou outra estratégia esperada?

