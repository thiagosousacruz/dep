# Sintaxe Basica, RDD, DAGs e Spark SQL (PySpark)

## O que e
Compreender como a maquina opera "por debaixo" antes de digitar codigos e fundamental. Diferente do ecossistema local do Python, o Spark orquestra lotes processuais por avaliacoes passivas. O framework tambem detem interoperabilidade brilhante permitindo aos desenvolvedores intercalar API Tabular com o glorioso SQL puro no codigo!

## Nivel Junior/Pleno: Lazy Evaluation (Transformations vs Actions)
Operacoes no Spark dividem-se em "Transformations" (que apenas adicionam instrucoes de memoria local) e "Actions" (que disparam a computacao fisica perante toda a fazenda do cluster engajando a execucao obrigatoria).

```python
from pyspark.sql.functions import col

# TRANSFORMATIONS (Avaliacao Preguicosa): Execucao instantanea porque nada ocorre no armazenamento fisico. O Spark traca um Grafo Aciclico (DAG).
df_filtrado = df_origem \\
    .filter(~col("nome").isNull()) \\
    .withColumn("idade_ajustada", col("idade") + 1)

# ACTIONS: O driver Spark Master orquestra os nodes escravos (Workers) para iniciar a leitura de fato.
df_filtrado.count()          # Retorna numero de linhas 
df_filtrado.show(10)         # Exibe uma amostra restrita no console
df_filtrado.write.save(...)  # Dispara a gravacao no Data Lake
```

## Evolucao da API (RDD vs DataFrame)
A API antiga (RDD) e verbosa e nao dispoe das otimizacoes nativas. A API moderna "DataFrame API" utiliza internamente o *Catalyst Optimizer* para repensar planos de acesso lógicos mais rapidos de alcancar discos.

```python
# O PADRAO DE MERCADO DATABRICKS (DataFrame API Otimizada)
df_vendas = spark.read.csv("/mnt/vendas.csv", header=True)
df_total = df_vendas.filter(col("status") == "FECHADO")
```

## A Ponte Interoperavel: Spark SQL e Temp Views
Voce pode pausar a abstracao programatura de DataFrame e rodar queries relacionais cruas no meio de uma transformacao, perfeito p pivoteamentos complexos e para alavancar membros que migram de Analise de Dados pro Engenho!

```python
# 1. Transformando o seu DataFrame Mutavel em uma Tabela Virtualizada SQL
df_python.createOrReplaceTempView("view_vendas_temporaria")

# 2. Executando SQL ANSI puro e devolvendo o output para a malha Python
df_resultado_sql = spark.sql("""
    SELECT 
        regiao,
        COUNT(*) as total_transacoes,
        SUM(valor) as receita
    FROM view_vendas_temporaria
    WHERE valor > 0
    GROUP BY regiao
""")

# VISTAS GLOBAIS DE ORQUESTRACAO (Cross-Cluster):
# Cria uma visao acessivel a TODOS os notebooks/sessoes ativos rodando nas outras abas do Cluster Databricks ao mesmo tempo!
df_cargas.createOrReplaceGlobalTempView("tb_acessivel_por_todos")
df_puxado_do_vizinho = spark.sql("SELECT * FROM global_temp.tb_acessivel_por_todos")
```

## Importacoes centrais da biblioteca
A arquitetura de bibliotecas obrigatorias instanciada nos scripts.

```python
# F-Native (Toda funcao matematica, filtros booleanos, casts rapidos e regex):
import pyspark.sql.functions as F

# T-Native (Descritores tipologicos fisicos no Dataframe Structs):
import pyspark.sql.types as T
```
