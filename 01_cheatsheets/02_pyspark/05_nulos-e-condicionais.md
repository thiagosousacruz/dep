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
Manipulacoes diretas mitigando nulos indiscriminados limitrofe. Observacao Critica: O expurgo via Dropna em Pipelines Gold deve ser acurado em escopo, evitando a desfragmentacao de informacao sadia contida em feature paralela da mesma row vitimada.

```python
# EXPURGACAO ESTRITA
# Remove apenas as linhas que detem nulo EXCLUSIVAMENTE nos pilares chaves listados (idade e cpf). Nulos perifericos em var de contato nao destruiriam a matriz row inteira. 
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
Divisao elementar como `df.lucro / df.custo` com custos operantes batendo fisicamente = 0 ocasionam `ZeroDivisionError` no node Spark derrubando a malha da DAG na Cloud!

```python
# Tratamentos logicos mitigam este rombo com defesoes Nativas.
df_fatoracao = df.withColumn(
    "rentabilidade",
    # Condiciona a quebra forcando o valor de falha gerar None local inves de travar!
    when(col("custos_de_producao") == 0, lit(None))
    .otherwise(col("receita") / col("custos_de_producao"))
)
```
