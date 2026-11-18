# Como o Spark executa seu código

> **Objetivo:** prever quando o Spark realmente processa dados, onde há shuffle e ler o essencial de um `explain`. **Tempo:** 1–2 h. **Pré-requisitos:** saber criar um DataFrame e usar `select`/`filter`/`groupBy`.

## O problema

Uma célula com dez transformações termina em milissegundos; depois um `count()` leva dez minutos. Outra pessoa "otimiza" trocando a ordem dos filtros e nada muda. Sem um modelo de execução, performance vira tentativa e erro e a depuração engana: o erro aparece na ação, não na linha que o causou.

## Modelo mental

- **DataFrame é uma receita, não um resultado.** Transformações (`select`, `filter`, `join`, `groupBy`) só descrevem o plano. Nada é lido até uma **ação** (`count`, `show`, `collect`, `write`, `display`).
- **O Catalyst reescreve a receita.** Antes de executar, o otimizador empurra filtros para perto da leitura, poda colunas e escolhe estratégias de join. Por isso reordenar filtros à mão raramente muda algo.
- **Ação → job → stages → tasks.** Cada ação gera um ou mais jobs. Um job é cortado em **stages** nas fronteiras de **shuffle**; cada stage roda uma **task por partição**.
- **Shuffle é redistribuir linhas pela rede** para que linhas com a mesma chave fiquem juntas. Transformações *narrow* (`select`, `filter`, `withColumn`) não precisam disso; *wide* (`groupBy`, `join` sem broadcast, `distinct`, `orderBy`, `repartition`) precisam.

```text
read → filter → withColumn ║ shuffle ║ groupBy/agg ║ shuffle ║ orderBy → write
└──────── stage 1 ────────┘           └── stage 2 ──┘          └─ stage 3 ─┘
         (narrow)          Exchange         (wide)    Exchange
```

No plano físico, cada shuffle aparece como um nó **`Exchange`**. Contar `Exchange` é a primeira leitura útil de um `explain`.

## Exemplo para prever

Antes de rodar, responda: (1) qual linha dispara processamento? (2) quantos `Exchange` o plano terá? (3) quantas etapas de agregação?

```python
from pyspark.sql import functions as F

vendas = spark.range(1_000_000).withColumn("loja", F.col("id") % 10)
da_loja_3 = vendas.filter(F.col("loja") == 3)
resumo = da_loja_3.groupBy("loja").agg(F.count("*").alias("qtd"))

resumo.explain("formatted")   # não processa dados, só mostra o plano
resumo.show()                 # ação: agora sim roda
```

Resultado esperado:

- Só o `show()` processa dados; as três atribuições e o `explain` são instantâneos.
- Um `Exchange hashpartitioning(loja, ...)`: o `groupBy` precisa juntar a mesma loja.
- **Dois** `HashAggregate`: um parcial antes do shuffle (cada partição conta localmente) e um final depois. Isso reduz o volume que trafega.
- O `Filter` aparece antes do `Exchange`: filtrar cedo diminui o shuffle.

Com AQE ligado (padrão no Databricks), o plano final pode mostrar `AdaptiveSparkPlan` e ajustes feitos em tempo de execução; o número de `Exchange` continua sendo o ponto de partida.

## Quebre de propósito

1. **Duas ações, dois jobs.** Rode `resumo.count()` duas vezes e observe na Spark UI: o trabalho é refeito. Sem cache, cada ação recalcula a receita inteira.
2. **Acrescente ordenação.** `resumo.orderBy("qtd").explain()` — surge um segundo `Exchange`, agora `rangepartitioning`. Ordenação global também é shuffle.
3. **Broadcast × sort-merge.** Crie `lojas = spark.createDataFrame([(3, "Centro")], "loja INT, nome STRING")` e compare os planos de `vendas.join(F.broadcast(lojas), "loja")` e `vendas.join(lojas.hint("merge"), "loja")`. O primeiro vira `BroadcastHashJoin`, sem `Exchange hashpartitioning`: a tabela pequena é copiada para cada executor. O segundo vira `SortMergeJoin`, com `Exchange` dos dois lados. Sem o hint, o Spark só escolhe broadcast sozinho quando conhece o tamanho da tabela, o que é comum em tabelas Delta e menos garantido em DataFrames criados no notebook.
4. **UDF Python bloqueia otimização.** Aplique `F.udf(lambda x: x * 2, "long")` em `id` e filtre pelo resultado. O plano ganha `BatchEvalPython`/`ArrowEvalPython` e o filtro não pode mais ser empurrado para a leitura.
5. **O erro aparece longe da causa.** Faça `withColumn("x", F.col("id").cast("int") / F.lit(0))` com ANSI ligado: a célula da transformação passa; o erro só surge no `show()`.

## Erros comuns e como diagnosticar

- **"A célula rodou rápido, então está certo."** → transformações não executam. Confirme com uma ação controlada (`count` em amostra, `limit` + `show`).
- **`count()` espalhado para depurar** → cada um é um job completo. Use em pontos de checagem deliberados e remova depois.
- **`collect()`/`toPandas()` em tabela grande** → traz tudo para o driver e pode derrubá-lo. Agregue ou limite antes.
- **Otimizar sem olhar o plano** → leia `explain("formatted")` e a Spark UI/Query Profile antes: conte `Exchange`, procure estratégia de join e UDFs.
- **Achar que `show()` mede o custo total** → ele pode processar só o necessário para exibir as primeiras linhas. Para medir, use a ação real (ex.: `write`).

## Cheque seu entendimento

1. Por que três transformações seguidas não geram nenhum job?
2. O que é um `Exchange` e por que ele separa stages?
3. Dê dois exemplos de transformação narrow e dois de wide.
4. Por que há dois `HashAggregate` em um `groupBy` simples?
5. Em que situação um join não precisa embaralhar a tabela grande?

## Próximos passos

- **Consulta:** [Transformações e ações](../01_cheatsheets/02_pyspark/01_fundamentos-dags-sql.md#transformacoes-e-acoes) · [Diagnóstico antes da otimização](../01_cheatsheets/02_pyspark/13_performance-e-arquitetura.md#diagnostico-antes-da-otimizacao) · [Shuffle, skew e spill](../01_cheatsheets/01_sql/12_performance-tuning.md#shuffle-skew-e-spill)
- **Prática:** [desafio de transformações e ações](../desafio.html?id=spk-01-transformacoes-acoes) · [desafio de diagnóstico](../desafio.html?id=spk-13-diagnostico) · [desafio de shuffle, skew e spill](../desafio.html?id=sql-12-shuffle-skew-spill)
- **Aplicação real:** abra um notebook autorizado que você já usa, rode `explain("formatted")` na consulta principal e anote: quantos `Exchange`, que estratégia de join e se há UDF Python. Explique o plano para alguém do time.
