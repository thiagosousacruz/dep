# Quality Operational Profiling (Data Quality em PySpark)

## O que e
As defesas analiticas para garantir saude referencial nas etapas Gold e Trusted (Analytics Engineering). E recomendado possuir uma camada isolada ou um framework leve que averigue desvios estatisticos de volumetria, comparativos em perdas de linhas em Join e metricas de esparsidade nulas operantes nas features antes do fechamento/commit real para os Datamarts e usuarios do painel.

## Verificacoes Preditivas Baseadas Eixos/Graos

```python
from pyspark.sql.functions import col, count, sum, countDistinct

# 1. VERIFICACAO DE EXTRUIDACAO DE GRAO E CHAVES (Unique Keys Rules)
# O script abaixo avalia se o Id_Transacao supostamente oficial da tabela permaneceu unitario na contagem e valida o gap. 
contagem_metrica = df_final.agg(
    count("*").alias("Tamanho_Total_Linhas"),
    countDistinct("id_transacao_chave_pk").alias("Chaves_Unicas_PK_Totais")
).collect()[0]

if contagem_metrica["Tamanho_Total_Linhas"] != contagem_metrica["Chaves_Unicas_PK_Totais"]:
    print(f"ALERTA SEVERO! O dataframe gerado deveria representar 1 row per transaction... Existem Transacoes Id duplicadas. Tamanho Rows: {contagem_metrica['Tamanho_Total_Linhas']} | Chaves: {contagem_metrica['Chaves_Unicas_PK_Totais']} ")
    # Pode Iniciar instrucao limitadora (ex. Raise Exception interrompendo o Jenkins Job)
```

## Perfilamento Contabil de Volume Nulo e Faltantes

```python
from pyspark.sql.functions import col, sum, when

# 2. CALCULO MATRICIAL E ESPECIFICO DO PESO NULO EM CAMPO CHAVE (Esparsividade Nula)
def checar_densidade_coluna(df, coluna_alvo):
    res_profiling = df.select(
        (sum(when(col(coluna_alvo).isNull(), 1).otherwise(0)) / count("*") * 100).alias("porcentagem_falta")
    ).collect()[0]
    
    return res_profiling["porcentagem_falta"]

indice_nulos_telefone = checar_densidade_coluna(df_base, "telefone_cliente")

if indice_nulos_telefone > 25.0:
    print("WARNING QUALITY: A coluna telefones esta vindo com + de 25% de buracos globais. Inviavel usar essa propensão para modelos de Ligacao Preditiva Marketing ML.")
```

## Conciliacao Pos-Join Cruzamento Origem/Destino (Drop Gaps)

```python
# 3. RECONCILIACAO E MATRIZ POS-INTERACAO (Verificar se perdemos dados bons de origem nas unioes acirradas do Inner Join com tabelas defeituosas dimensionais!)

linha_tamanho_fonte_A = df_Origem_Legado.count()
linha_tamanho_cruzada = df_inner_joinado_com_B.count()

qnt_linhas_orfades = linha_tamanho_fonte_A - linha_tamanho_cruzada

if qnt_linhas_orfades > (linha_tamanho_fonte_A * 0.10):
     # Tolerancia max: Nao se pode perder mais de 10% da origem tentando cruzar em tabelas dimensionais!
    raise ValueError(f"FALHA DQ FATAL! Perda abusiva no INNER JOIN. A Tabela B não acompanhou a massa da A e descartou mais de 10% das Vendas originais limitando o DataMart!")
```
