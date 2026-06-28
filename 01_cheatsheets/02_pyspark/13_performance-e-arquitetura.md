# Performance Tuning, Arquitetura DevOps e Testes (PySpark)

## O que e
As fronteiras do Arquiteto Big Data. O Tuning mitiga a ociosidade ou afundamento (OOM) de processadores repensando as malhas distribuidas de memoria (Shuffles e AQE). Já a infraestrutura DevOps aborda agnosticismo de códigos (Separation Of Concerns), e testes em Mock de CI/CD para que lógicas Spark ganhem escala e integridade produtiva.

## 1. Otimização Adaptativa (AQE) e Redistribuicao de Carga
As extensoes operantes configuraveis na sessao do databricks em versoes 3.X que alteram planos em *Runtime* baseado na observacao em disco.

```python
# 1.1 CONFIGS DO DATABRICKS ADAPTATIVE:
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")

# 1.2 SHUFFLE VOLUNTARIO: REPARTITION E COALESCE
# REPARTITION (Mixagem Universal). Custa extrema latencia. Destroi limites ordenados para balancear bits igualmente as Cpus.
df_nivelado_p_join = df_assimetrico.repartition(400, "codigo_uf")

# COALESCE (Compreensao Pacífica). Une partições pequenas esparsamente fracas apertando-as pra dentro nas partições contiguas MAIORES sem mandar pacotes pesados transitar pelo fio!
df_final_comprimido_clean = df_apos_filtros.coalesce(20)
```

## 2. Solucao de Skew Joins In-Memory (Salting e DPP)
Se atrelar Data-Skews em Joins quebra nodes independentes mesmo com repatition, fatiamos de vez.

```python
from pyspark.sql.functions import rand, lit, explode, array

# SALTING ARTIFICIAL:
# Uma chave "STATUS=OK" detem bilhoes de ocorrencias e afundou uma CPU sozinha.
# Injetamos valores aleatorios (Salt 0-9) espalhando artificialmente o Skew!
df1_salteado = df_estourada.withColumn("salt", (rand() * 10).cast("int"))
df2_alvo_salteado = df_dimensao.withColumn("salt", explode(array([lit(i) for i in range(10)])))

df_cruzamento = df1_salteado.join(df2_alvo_salteado, ["chave_original", "salt"]).drop("salt")

# DYNAMIC PARTITION PRUNING (DPP): Otimizacao fantastica!
# Cortes automaticos de particoes antes do Join comecar a ler a Fato baseada na Chave da tabela dimensional que sequer será batida (Injeção via Filter Pre-Scan).
spark.conf.set("spark.sql.optimizer.dynamicPartitionPruning.enabled", "true")
```

## 3. Vetores Apache Arrow (Pandas UDFs)
Uso de funcoes comuns Python (`def()`) encapsuladas em `udf` matam operabilidades (Byting Row by Row). Substituir logicas dificeis em pythons nativas por Vetores Pandas (Mecanica C++ in RAM) acelera lotes brutais.

```python
from pyspark.sql.functions import pandas_udf
import pandas as pd
from pyspark.sql.types import StringType

# The Silver Bullet:
@pandas_udf(StringType())
def tag_vetorizada_operacao(serie_recebida_memoria_em_lotes: pd.Series) -> pd.Series:
    # A aplicacao rodará Batch Vectors ignorando serializacao limitante
    return serie_recebida_memoria_em_lotes.apply(lambda val: "VIP" if val > 2500000 else "STANDART")

df_tunado_vector = df_estourado_lento.withColumn("classificacao", tag_vetorizada_operacao("saldo"))
```

## 4. Separation of Concerns (OOP) e Loggings
Isolar chamadas Cloud de Arquiteturas matemáticas previne spaghettificacão de paineis iterativos de cadernos.

```python
import os
import logging
from pyspark.sql.functions import col

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

# THE CONFIG MAGNAGER (Parametros injetados por ADF Ditando Alvos em RunTime)
class VariaveisPipeline:
    def __init__(self):
        self.ambiente = os.getenv("RUNNING_ENV", "dev")
        self.path_alvo = f"/mnt/{self.ambiente}/bronze/estoques"

CONF = VariaveisPipeline()

# THE AGNOSTIC MATH: Função imutavel Pura (Não Encosta Em Banco pra não travar!)
def aplicar_lucratividade(df_entrada):
    return df_entrada.withColumn("imposto", col("vlr_custo") * 0.17)

def main_job():
    LOG.info("Start!")
    df_base = spark.read.parquet(CONF.path_alvo) 
    df_imposto = aplicar_lucratividade(df_base)   
    LOG.info("Escrita ok.")
```

## 5. Mock Sessions CI Locais (Pytest)
Nao teste lógicas matemáticas pagando Databricks. Crie mini clusters in memory para Esteira Jenkins/Github testando as regras cegas em mocks arrays gerados em terminal!

```python
## Arquivo: '/tests/test_tributacao.py'  
import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, DoubleType

from projeto.modulo_tributacao import aplicar_lucratividade

# 1. FIXTURE SERVERLESS (Driver Mode in RAM, isolado).
@pytest.fixture(scope="session")
def fake_session():
    return SparkSession.builder.master("local[1]").appName("teste_cicd").getOrCreate()

# 2. SEU CÓDIGO TESTADO VIA CHECK CI
def test_validacao_regrad_de_tributo_aplicada_ascedente(fake_session):
    
    # DATAFRAMES FALSOS:
    esquema_tabela = StructType([ StructField("vlr_custo", DoubleType()) ])
    df_mock = fake_session.createDataFrame([(100.0,)], esquema_tabela)
    
    # ALGORITMO:
    res_df = aplicar_lucratividade(df_mock)
    rows_nativo = res_df.collect()
    
    # 100 * 0.17 % ICMS = 17 !!!
    assert rows_nativo[0]["imposto"] == 17.0
```
