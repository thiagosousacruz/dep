# Diagnóstico de performance: medir antes de mexer

> **Objetivo:** seguir uma sequência de diagnóstico, reconhecer skew, spill e excesso de shuffle nas evidências e escolher uma intervenção proporcional. **Tempo:** 2 h. **Pré-requisitos:** [Como o Spark executa seu código](05_como-o-spark-executa.md).

## O problema

O job que levava 10 minutos agora leva 50. A reação comum é aumentar o cluster, trocar `repartition` por `coalesce` ou copiar uma configuração de um fórum. Às vezes melhora, às vezes piora, e ninguém sabe por quê. Performance se resolve com evidência: **onde** o tempo está sendo gasto e **qual** é a causa.

## Modelo mental

Quase todo problema de performance em Spark cai em quatro causas:

```text
Causa                 Evidência típica                             Primeira intervenção
Ler demais            muitos bytes/arquivos lidos; sem pruning     filtro na partição/cluster, projeção, layout
Embaralhar demais     muitos Exchange; shuffle grande              broadcast do lado pequeno, agregar antes
Skew                  poucas tasks muito mais lentas que a mediana tratar chave quente, AQE skew join, salting
Spill / memória       "spill (disk)" nas métricas; tasks pesadas   partições menores, menos dados por task
```

- **Spark UI / Query Profile:** compare duração **máxima** e **mediana** das tasks de um stage. Se a máxima for muito maior, há skew; se todas forem lentas, o problema é volume ou leitura.
- **AQE** (ligado por padrão no Databricks) ajusta o plano em tempo de execução: junta partições pequenas depois do shuffle, divide partições com skew em joins e pode trocar a estratégia do join.
- **Agregação parcial protege `groupBy`.** `count` e `sum` calculam um parcial antes do shuffle, então a chave quente vira uma linha por partição. O skew dói de verdade em **joins**, **janelas** e agregações que guardam linhas (`collect_list`).
- **Uma mudança por vez**, sempre conferindo se o resultado continua o mesmo.

## Exemplo para prever

```python
from pyspark.sql import functions as F

# 90% das vendas na loja L0
vendas = spark.range(1_000_000).withColumn(
    "loja",
    F.when(F.col("id") < 900_000, F.lit("L0"))
     .otherwise(F.concat(F.lit("L"), (F.col("id") % 9 + 1).cast("string"))),
)

# 1. Frequência das chaves
vendas.groupBy("loja").count().orderBy(F.desc("count")).show(3)

# 2. Linhas por partição quando distribuímos pela chave
(vendas.repartition(8, "loja")
    .groupBy(F.spark_partition_id().alias("particao")).count()
    .orderBy(F.desc("count")).show())
```

Antes de rodar: qual é a maior partição no passo 2? Quantas partições ficam vazias?

Resultado esperado (Spark local):

- Passo 1: `L0` com 900.000 e as demais com cerca de 11.000.
- Passo 2: **uma partição com 900.000 linhas** e as outras com no máximo algumas dezenas de milhares. Com 10 chaves e 8 partições, algumas partições ficam vazias. É assim que um stage fica preso numa única task.

Em SQL, o primeiro passo é o mesmo:

```sql
SELECT loja, count(*) AS n FROM vendas GROUP BY loja ORDER BY n DESC LIMIT 20;
```

## Quebre de propósito

1. **Salting.** Acrescente `sal = id % 8` e distribua por `("loja", "sal")`. A maior partição cai de 900 mil para algo como 240 mil, mas **não fica perfeitamente equilibrada**: o hash de poucas combinações em poucas partições colide. Salting ajuda, não faz milagre.
2. **Agregação em duas etapas.** Some por `(loja, sal)` e depois por `loja`. O resultado tem de ser idêntico ao `groupBy("loja")` direto. Se não for, o salting quebrou a lógica.
3. **Veja o AQE agir.** Rode `vendas.groupBy("loja").count().collect()` e depois `explain()`. O plano final mostra `AdaptiveSparkPlan isFinalPlan=true` e `AQEShuffleRead coalesced`: das 200 partições de shuffle configuradas, o AQE juntou as quase vazias.
4. **Broadcast como alternativa ao salting.** Se o join com skew é contra uma tabela pequena (`dim_loja`), compare o plano com `F.broadcast(dim_loja)`. Sem shuffle do lado grande, o skew deixa de importar para esse join.
5. **`coalesce(1)` antes de escrever.** Compare o número de tasks do stage de escrita com e sem ele. Tudo passa a rodar numa task só, e partições "ajeitadas" no fim podem desfazer o paralelismo do pipeline inteiro.

## Erros comuns e como diagnosticar

- **Aumentar o cluster contra skew** → a task da chave quente continua sozinha, só que com mais máquinas ociosas. Confira máxima × mediana das tasks antes.
- **Salting como primeira opção** → aumenta a complexidade e o volume (o lado replicado é multiplicado). Antes, tente filtrar a chave quente (nulos, `'N/A'`, cliente genérico), usar broadcast e o skew join do AQE.
- **Chave quente = valor "lixo"** → muitas vezes o skew é `NULL` ou um código padrão. Trate isso antes de qualquer tuning.
- **Mexer em `spark.sql.shuffle.partitions` sem medir** → com AQE, partições pequenas já são juntadas. No serverless, várias configurações nem podem ser alteradas.
- **Comparar tempos com cache quente ou cluster diferente** → meça nas mesmas condições e registre bytes lidos, shuffle e spill, não só o tempo.

## Cheque seu entendimento

1. Quais quatro causas você investiga primeiro, e qual evidência aponta para cada uma?
2. Por que um `groupBy().count()` sofre pouco com skew e um join sofre muito?
3. O que o AQE faz com as partições depois de um shuffle?
4. Por que salting não garante partições equilibradas?
5. Que métrica da Spark UI mostra skew?

<details markdown="1">
<summary>Respostas</summary>

1. Ler demais (muitos bytes/arquivos, sem pruning), embaralhar demais (muitos `Exchange`, shuffle grande), skew (poucas tasks muito mais lentas que a mediana) e spill/memória (`spill (disk)` nas métricas).
2. A agregação parcial reduz a chave quente a uma linha por partição antes do shuffle. No join, todas as linhas da chave quente precisam ir para a mesma task.
3. Junta partições pequenas depois do shuffle (coalesce), divide partições com skew em joins e pode trocar a estratégia de join em tempo de execução.
4. Ele espalha a chave quente em N pedaços, mas cada pedaço ainda pode ser maior que as chaves comuns, e o hash pode colocar vários pedaços na mesma partição. Diminui o pior caso (no exemplo, de 900 mil para cerca de 240 mil), mas não iguala.
5. No resumo das tasks do stage: a duração **máxima** (e o shuffle read máximo) muito acima da **mediana**.

</details>

## Próximos passos

- **Consulta:** [Sequência de diagnóstico](../01_cheatsheets/01_sql/12_performance-tuning.md#sequencia-de-diagnostico) · [Shuffle, skew e spill](../01_cheatsheets/01_sql/12_performance-tuning.md#shuffle-skew-e-spill) · [AQE e partições](../01_cheatsheets/02_pyspark/13_performance-e-arquitetura.md#aqe-e-particoes) · [Skew e salting](../01_cheatsheets/02_pyspark/13_performance-e-arquitetura.md#skew-e-salting)
- **Prática:** [sequência de diagnóstico](../desafio.html?id=sql-12-sequencia-diagnostico) · [AQE e partições](../desafio.html?id=spk-13-aqe-particoes) · [skew e salting](../desafio.html?id=spk-13-skew-salting) · [pruning e pushdown](../desafio.html?id=sql-12-pruning-pushdown)
- **Aplicação real:** escolha o job autorizado mais lento que você acompanha. Registre os bytes lidos, o maior stage, máxima × mediana das tasks e o spill. Proponha **uma** mudança e meça antes e depois.
