# Janelas e Funcoes Relacionais (Window Functions em PySpark)

## O que e
As janelas de agrupamento transitorio analitico mitigam a perda horizontal que `group_by()` causaria na tabela. Sem aglutinar a base verticalmente, a *Window Specification API* fornece sub-grupos isolados por registro na linha de execucao de ranking nativo ou variaveis sequenciais defasadas (`Lags / Leads / Sum() Over`).

## Nivel Junior/Pleno: Instanciamento O-O (Row Numbers Analiticos)
Deduplicacoes ou rankings rigorosos perante linhas identicas de log necessitam declarar o espectro de atuacao na janela antecedente de uso.

```python
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number, col

# 1. Definicao do "Container" Base da Janela: A regra de contagem e ordencao de recencia
wdw_especificadora = Window \\
    .partitionBy("id_dispositivo") \\
    .orderBy(col("data_extracao_utc").desc())  # Ultima ocorrencia = Top 1 na iteracao da row

# 2. Desdobramento In-Loco na Tabela
df_purificado = df_logs_duplicados \\
    .withColumn("indexacao_rank", row_number().over(wdw_especificadora)) \\
    .filter(col("indexacao_rank") == 1) \\
    .drop("indexacao_rank") 
```

## Nivel Pleno: Metricas Progressivas (Lags/Leads e Acumuladores YTD)
Desvios matematicos fundamentados no espacamento retroativo do eixo tempo num usuario. Ex: Qual a metrica gerada na diferenca da acao atual contra o clique exato registrado duas etapas atras (Lead/Lag).

```python
from pyspark.sql.functions import lag

# Janela expandida base: Qual a ordem natural dos eventos?
wdw_time_series = Window.partitionBy("user_hash").orderBy("data_clique_ts")

df_comportamental = df_fatos \\
    .withColumn(
        "saldo_verificado_visita_anterior",
        # Lag recua virtualmente `N` steps ordenados dentro do WindowSpec listado atual. 
        lag(col("saldo_corrente"), 1).over(wdw_time_series)
    ) \\
    .withColumn(
        "delta_gasto_do_cliente",
        (col("saldo_corrente") - col("saldo_verificado_visita_anterior"))
    )
```

## Sênior Alvo: Range Frames Fixos Restritos e Amarras de OOM
Restringir espacamentos deslizantes vigorosamente previne exaustao dos logs em master limitando as operacoes que uma acao em Fila obriga as threads carregarem em Ram Virtual.

```python
from pyspark.sql.functions import avg

# Range Manual Restrito por Janela (Ex: Media Movel da Semana Fechada).
# Enclausuramos o comportamento iterativo para englobar unicamente as seis ocorrencias previas limitadas acopladas mais a atual.
wdw_deslizantes_7_dias_moveis = Window \\
    .partitionBy("segmento") \\
    .orderBy("data_referencia") \\
    .rowsBetween(-6, Window.currentRow)  # Base segura fechada. (Window.unboundedPreceding e infinitiva e perigosa logica massiva)

df_tendencia = df_movimentacao \\
    .withColumn("historico_media_movel_vendas", avg("venda").over(wdw_deslizantes_7_dias_moveis))
    

# ALERTA VERMELHO CRITICO DE OOM: NUNCA INICIE OU DEFINA A PROPRIA WINDOW DA DAG SEM O BLOCO 'PARTITION BY'! Invocando Window.orderBy("ano_fiscal") global forcará o Catalyst de Big Data a estrangular TODO O CLUSTER de Terabytes pra cima de um Unico Worker de Particao Master visando garantir o sorteio perfeitamente linear, estourando processamento irreversivel!
```
