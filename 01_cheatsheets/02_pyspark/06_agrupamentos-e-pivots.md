# Agrupamentos, Agregacoes e Pivots (PySpark)

## O que e
Nucleo das analises metricas, consolidando dataframes detalhados ou transacionais num target relacional sumarizado e gerencial. Transitar entre eixos de tuplas verticais via transforamoes pivotantes assegura compatibilidades cruzadas complexas para ML e Dashboards.

## Nivel Junior/Pleno: Dicionarios de Agg e Atalhos de Cloud
Evite fracionamentos sucessivas invocando instanciacoes singulares. Uma unica passada em metodo agregador contendo list comprehension de importacoes performaticas e ideal!

```python
from pyspark.sql.functions import sum, avg, count, round, approx_count_distinct, count_if

df_sumarizado = df_fatos \\
    .groupBy("ano_fiscal", "uf_estado") \\
    .agg(
        # 1. Contadores base:
        # Nota: O uso do .agg() generalista em tudo (Exemplo Total Table Scan sem agrupar): df.agg(sum('balanco')) 
        count("id_transacao").alias("volume_vendas"),
        
        # 2. Equacoes Analiticas Diretas In-Scope:
        round(avg("lucro_total"), 2).alias("ticket_lucrativo_medio"),
        
        # 3. Agrupadores com Filtro (Spark Nativo). 
        # Isola a sub-equacao de restricoes sem necessitar de When/Otherwise
        count_if(col("status_flag") == "ERRO").alias("falhas_do_estado"),
        
        # 4. A MAGIA APROXIMADA DA CLOUD EXTREMA
        # Para big data extremo, o count_distinct exato sofre gargalos astronomicos no Memory Sort. Use o 'approx', calcado em probabilismo (Erros marginaveis na media de ~2%) e velocidade assombrosa.
        approx_count_distinct("hash_cliente").alias("clientes_unicos_aprox")
    )
```

## Nivel Senior: Operacoes de Transposicao (Pivot e Melt)
O analista ou gerencia anseia a transformacao limitadora vertical. Onde os dados se estendam em Colunas fisicas independentemente extraidas por grupo gerado no group. 

```python
# PIVOTAMENTO
# Exige-se restricoes em formato Lista dura(Hard-code), inviabilizando processamento lento de auto-discovery que o Spark detesta nas colunas dinâmicas em discos analiticos!
df_pivotado = df_logistica \\
    .groupBy("produto_categoria") \\
    .pivot("ano_ocorrencia", [2022, 2023, 2024]) \\
    .agg(sum("receita_consolidada"))
# Output -> | produto_categoria | 2022 | 2023 | 2024 |

# UNPIVOT (MELTING) em Spark 3.4+
# Processo inverso. Achata colunas expandidas transformando numa relacional normalizada com label das chaves. Ideal pare limpezas pos dumps Excel.
df_normalizado = df_metricas_bizarras_excel \\
    .unpivot(
        ["regiao_loja"],                     # Ancoras fixadas imutaveis (IDs da linha mantido)
        ["receita_jan", "receita_fev"],      # Vitimas (As colunas q tombarão)
        "Label_Base_Mes",                    # Alias da nova coluna referenciado o ex-nome do vitima 
        "Faturamento_Aferido"                # Alias da nova coluna alojando o conteudo interno dele  
    )
```
