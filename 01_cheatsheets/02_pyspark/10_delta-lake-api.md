# Protocolo Delta Table API Programática (PySpark)

## O que e
O Delta Lake é uma camada transacional operando encima dos dados Parquets no storage, mantendo metadados unificados para lidar com concorrência. Utilizar sua integracao programática orientada a objetos (DeltaTable) é mandatório para `upserts` em notebooks analiticos sem utilizar Strings difíceis no `spark.sql()`.

## Nivel Pleno: Execuções CDC Upserts Limpas (Merge Into)
Evitem recargas massivas diárias estaticas. Inspecione metadados cruzaveis e integre condicoes de mutação limpa (A Base Insere dados Novos e Atualiza os já Vistos).

```python
from delta.tables import DeltaTable
from pyspark.sql.functions import current_timestamp

# Instanciando o Alvo Final Master persistido nos discos Delta
alvo_fisico_Delta = DeltaTable.forName(spark, "lakehouse_gold.Tb_Fatos_Base_Corporativa")

# Construção Programática CDG Genérica
alvo_fisico_Delta.alias("tabela_target").merge(
    df_lote_hoje.alias("lote_source"),
    "tabela_target.chave_primaria_unica = lote_source.chave_primaria_unica"
) \\
.whenMatchedUpdateSet( # SE Encontrou Ocorrencia Existente de Chave, Faça Updates!
    { "financeiro": "lote_source.faturamento_atual", "updatetime": "current_timestamp()" }
) \\
.whenNotMatchedInsertValues( # Ocorrencias Novas Omitidas DoTarget? Faça Instancia Absoluta!
    { "chave_primaria_unica": "lote_source.chave_primaria_unica", "financeiro": "lote_source.faturamento_atual" }
) \\
.execute()
```

## Evolucao Adaptativa de Schemas (Merge Schema)
Ao longo dos meses do projeto, novos times Ingerem Metadados inéditos do CRM. Ate entao sua Tabela Silver limitava as colunas e inserções estourariam `columns mismatch`. 

```python
# O MOTOR AUTOMATICO DE EVOLUCAO
# Adicionará pacificamente no dicionario Json da DeltaTable as chaves nascedouras sem comprometer o passado formativo!
df_com_colunas_novas.write \\
    .format("delta") \\
    .mode("append") \\
    .option("mergeSchema", "true") \\
    .save("/mnt/silver/tabela_mestra")

# CUIDADO: Permite INSERÇÃO de NOVOS. Mutação de um Tipo Original validado (Int pra String de supetão) continuará travando para proteger o ambiente O-O!
```

## Operabilidades de Administracao (Vacuum e Time Travel)
O Delta arquiva em Transacoes Logicas de Time Line mantendo seguranca na cloud contra DDLs Corruptas. Efetuar Maintences rotineiros varrem os bytes defasados.

```python
tbtarget = DeltaTable.forPath(spark, "/mnt/lake/gold/tb_fatos_base")

# 1. TIME TRAVEL / RESTORE MASTER: Destruiu a Fato base sem where num update? Basta Voltar 2 dias logicos sem recorrer ao BKP da Engenharia:
tbtarget.restoreToTimestamp("2024-05-18 01:00:00")

# 2. OTIMIZACAO DE SMALL FILES: Arquivinhos gerados de inserts minúsculos soltos ao longo da semana perdem paralelismo disk i/o. Zipelos!
tbtarget.optimize().executeZOrderBy(["uf_federativa", "regiao_centro_custo"])

# 3. VACUUM GARBAGE COLETOR: Vc realizou 18 Merge Intos neste mes gerando historicos fantasmas Delta consumindo FATURAS do AZURE STORAGE? Purifique.
# Ex: Retera metadados fantasmas para apenas dos Ultimos 7 dias (168 HORAS). Dados novos validados continuam operantes perfeitamente.
tbtarget.vacuum(168)  
```
