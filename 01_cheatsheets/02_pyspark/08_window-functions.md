# Window Functions em PySpark

> **Aprenda o conceito:** trilha [Window functions](../../03_trilhas/03_window-functions.md) — modelo mental, exemplo para prever e erros comuns.

## O que são

Uma `WindowSpec` define o grupo lógico, a ordenação e o frame usados por funções como `row_number`, `lag` e agregações acumuladas.

## Deduplicação determinística

```python
from pyspark.sql import functions as F
from pyspark.sql.window import Window

por_dispositivo = Window.partitionBy("dispositivo_id").orderBy(
    F.col("extraido_em").desc(),
    F.col("evento_id").desc(),
)

df_atual = (
    df_eventos
    .withColumn("ordem", F.row_number().over(por_dispositivo))
    .filter(F.col("ordem") == 1)
    .drop("ordem")
)
```

O desempate evita escolher linhas arbitrárias quando timestamps são iguais.

## Lag e acumulado

```python
ordem_cliente = Window.partitionBy("cliente_id").orderBy("evento_em", "evento_id")

df_variacao = df_eventos.withColumn(
    "valor_anterior",
    F.lag("valor").over(ordem_cliente),
)

acumulado_conta = (
    Window.partitionBy("conta_id")
    .orderBy("data_movimento", "movimento_id")
    .rowsBetween(Window.unboundedPreceding, Window.currentRow)
)

df_saldo = df_movimentos.withColumn("saldo", F.sum("valor").over(acumulado_conta))
```

## Frames e tempo

```python
ultimas_sete_linhas = (
    Window.partitionBy("segmento")
    .orderBy("data_referencia")
    .rowsBetween(-6, Window.currentRow)
)
```

Esse frame cobre sete linhas, não sete dias. Se houver datas ausentes ou múltiplas linhas por dia, agregue previamente no grão diário ou use um `rangeBetween` coerente com a expressão numérica de ordenação.

## Cuidados de escala

Uma janela ordenada sem `partitionBy` cria uma partição lógica global. Isso pode ser correto para ranking global, mas concentra a ordenação; confirme o custo no plano e na Spark UI. Acrescentar uma partição artificial muda a semântica e não é uma correção neutra.

- Observe skew e volume dentro de cada grupo.
- Reduza colunas antes da janela quando possível.
- Use ordem determinística.
- Meça sort, shuffle e spill.

## Checklist

- [ ] Partição e ordenação representam a regra de negócio?
- [ ] Empates têm critério explícito?
- [ ] O frame significa linhas ou intervalo de valores como pretendido?
- [ ] O tamanho das partições foi observado?

