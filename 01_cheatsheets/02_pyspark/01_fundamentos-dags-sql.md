# Sintaxe Basica, RDD, DAGs e Spark SQL (PySpark)

## O que e
Compreender como a maquina opera "por debaixo" antes de digitar codigos e fundamental. Diferente do ecossistema local do Python, o Spark orquestra lotes processuais por avaliacoes passivas. O framework tambem detem interoperabilidade brilhante permitindo aos desenvolvedores intercalar API Tabular com o glorioso SQL puro no codigo!

## Nivel Junior/Pleno: Lazy Evaluation (Transformations vs Actions)
Transformações descrevem um novo plano lógico e são avaliadas de forma lazy. Actions solicitam um resultado ou escrita e disparam os estágios necessários do plano.

```python
from pyspark.sql.functions import col

# TRANSFORMATIONS (Avaliacao Preguicosa): Execucao instantanea porque nada ocorre no armazenamento fisico. O Spark traca um Grafo Aciclico (DAG).
df_filtrado = df_origem \\
    .filter(~col("nome").isNull()) \\
    .withColumn("idade_ajustada", col("idade") + 1)

# ACTIONS: o driver coordena a execução das tarefas nos executores e materializa o trabalho necessário.
df_filtrado.count()          # Retorna numero de linhas 
df_filtrado.show(10)         # Exibe uma amostra restrita no console
df_filtrado.write.save(...)  # Dispara a gravacao no Data Lake
```

## Evolucao da API (RDD vs DataFrame)
RDDs oferecem controle de baixo nível, mas não expõem ao Catalyst a mesma informação estrutural disponível em DataFrames. Para transformações tabulares, a DataFrame API costuma permitir otimizações como poda de colunas, pushdown de filtros e seleção de estratégias físicas.

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
# Uma global temp view fica no banco global_temp e pode ser acessada por sessões ligadas à mesma aplicação Spark; não é persistente nem substitui uma tabela compartilhada.
df_cargas.createOrReplaceGlobalTempView("tb_acessivel_por_todos")
df_puxado_do_vizinho = spark.sql("SELECT * FROM global_temp.tb_acessivel_por_todos")
```

## Importacoes centrais da biblioteca
Importe apenas as funções usadas e prefira aliases consistentes no projeto.

```python
# F-Native (Toda funcao matematica, filtros booleanos, casts rapidos e regex):
import pyspark.sql.functions as F

# T-Native (Descritores tipologicos fisicos no Dataframe Structs):
import pyspark.sql.types as T
```
