# Nulos e Condicionais de Decisao (PySpark)

## O que e
O tratamento estrutural de lacunas. Assim como no ambiente relacional, valores "Nulos" implicam ausencia restrita de registros. Permitir a disseminacao nao mapeada de Nulos resulta em anomalias como agrupadores falhos e joins silenciosamente bloqueados (vazios nao equivalem logicos sem diretivas de metodos abertos).

## Nivel Junior/Pleno: Condicionais Case/When
Estrutura direcional vital para enriquecer caracteristicas derivadas evitando codigos `IF/ELSE` em blocos estritos e custosos de operacao local.

```python
from pyspark.sql.functions import col, when, coalesce, lit

df_classificado = df_vendas.withColumn(
    "classificacao_entrega",
    # O when substitui perfeitamente condicoes extensas in-loco
    when(col("prazo_dias") <= 3, "EXPRESSA")
    .when((col("prazo_dias") > 3) & (col("status_venda") == 'PAGA'), "RESTRITA")
    .otherwise("STANDARD") 
)

# ABSTRACAO SEGURA EM DIMENSOES (Fallback de Nulo)
# Em joins estreitos ou apresentacoes de Dashboards, remova o visual nulo provendo chaves falsas com Coalesce (Sempre Pega O Primeiro Valor Nao-Nulo da lista array esquerda p direita).
df_seguro = df_classificado.withColumn(
    "categoria_id_fixa",
    coalesce(col("categoria_original"), lit(-1)) # Adota numero -1 logico quando ausencia fisica for achada.
)
```

## Operadores de Sanitizacao Nativa: fillna e dropna
`dropna` remove linhas e pode descartar informação válida em outras colunas. Restrinja o subconjunto às colunas exigidas pela regra e acompanhe quantas linhas foram removidas.

```python
# EXPURGACAO ESTRITA
# Remove linhas com nulo nas colunas exigidas pela regra.
df_tratado = df_logistica.dropna(
    how="any",         
    subset=["idade", "cpf"] 
)

# PREENCHIMENTO POR DICIONARIO (Imputacoes Default)
# Substituicoes condicionais rapidas balizadas pelo dict do dev.
df_imputado = df_logistica.fillna({
    "idade": 0,                     
    "email": "SUPORTE@NOTFOUND.COM",
    "valor_final": 0.0              
})

# REPLACE COMUM A VAZIOS FANTASMAS STRING (Nulo vs Empty String)
# Empty Strings ( "" ) NÂO CAEM NAS REDES DO FILLNA E ISNULL!! Você os pega cruzando replaces brutos neles primeiro!
df_replaced = df_imputado.replace(["N/A", "NA", " ", ""], None) 
```

## Nivel Senior: Quality Blocks para Divisoes Analiticas
O comportamento de divisão por zero depende do tipo e da configuração ANSI. Expresse a política desejada para não depender do default da sessão.

```python
# Tratamentos logicos mitigam este rombo com defesoes Nativas.
df_fatoracao = df.withColumn(
    "rentabilidade",
    # Retorna NULL quando o denominador é zero.
    when(col("custos_de_producao") == 0, lit(None))
    .otherwise(col("receita") / col("custos_de_producao"))
)
```
