# Transformacoes e DataFrame API Expressiva (PySpark)

## O que e
Agrupador base do motor diário do Engenheiro de Dados. Varrendo desde seleções básicas (`select/withColumn`), filtros Booleanos lógicos sem perda estrutural (`filter`), manipulações operacionais contínuas da API analítica (`distinct/unionByName`) e saneamentos via `regex` e datas nativas. Pyspark abole updates-in-place focando em method chainings.

## Nivel Junior/Pleno: Seleção, Adição e Expressoes em String (SelectExpr)
Mapeando lotes, criando metadados colunares virtuais e atribuindo nomeclaturas limpas.

```python
from pyspark.sql.functions import col, lit

df_estrutural = df_base \\
    # PROJECAO (Restringe a apenas os citados)
    .select("cliente_id", "nome", "celular") \\
    
    # LITERAIS ESTATICOS (Insere strings ou ints fixos sem ser lidos do disco!)
    .withColumn("sistema_alocador_v1", lit("CRONOS_MASTER_JOB")) \\
    
    # ALIAS EM AMBIGUIDADES (Declara pre fixos logicos isoladores qnd formos dar join nas frentes com tabelas iguals B)
    .alias("Fato_A") \\
    
    .withColumnRenamed("cliente_id", "id_pk") \\
    .drop("celular", "outros")
    
# SELECTION EXPR IN-INLINE (Atalhos do SQL nativo numa string p limpezas sem ter de dar import col())
df_atalho_rapidaço = df_bruto.selectExpr("id_pk AS ID", "CAST(faturamento AS INT)", "ano_atual - 2000 AS dif_anos")
```

## Nivel Pleno: Filtros, Deduplicaçoes, Ordernaçoes, e Empilhamentos
Técnicas latescentes de limpeza, sampleamento produtivo para testes e unificação de layouts horizontais.

```python
# 1. FILTRAGEM BOOLEAN MULTIPARAM (Use parenteses ( x ) | ( z ) senao o '&' binario nativo crasha os bits)
df_restringido = df_estrutural.filter( 
    (col("nome").isNotNull()) & 
    (col("celular") != '') | 
    (col("status").isin(["VIP", "GOLD"]))
)
# ( O Operador Negação Global é Mapeado com `~`)    
df_saneados = df_restringido.filter(~col("status").isin(["BANIDO"]))

# 2. DROP DUPLICATES GERAIS E ORDENAÇÃO FOCAL:
# OrderBy aciona shuffles de partições de dados pra gerar matriz perfeitamente ordenada global. Custo Alto.
df_livre_repeticoes = df_saneados \\
    .orderBy(col("ano").desc(), col("faturamento").asc()) \\
    .dropDuplicates(["id_pk", "documento"]) # Elimina replicantes, escorando-se na PK, mantendo a "primeira vistar/ordem"

# 3. EMPILHAMENTOS DE LOTE (Union) E AMOSTRAGENS (Samples)
# Encenar 1 Terabyte para testar na maquina se quebra = Pessimo. Gere 'samples' fatiados seguros !
df_painel_amostral = df_mes_frio.sample(withReplacement=False, fraction=0.01, seed=42)

# Unificar Meses diferentes empilhando perfeitamente MESMO que a coluna ID num arquivo A esteja "fora da sua casa" na Posicao Z do arquivo B. (Ele cruza posicoes baseadas nos Nomes da Header).
df_history_complecion = df_janeiro.unionByName(df_fevereiro, allowMissingColumns=True) 
```

## Nivel Senior: Transformadores Temporais e Regex
Removendo a necessidade imperativa de pacotes arcaicos UDF pythons como `.datetime()`, lidando no motor C purista pra manipulações textuais brutas e saltos logicos em dias cruzados cronologicamente.

```python
from pyspark.sql.functions import current_date, date_add, datediff, regexp_replace, translate, trim, upper

df_limpezas_avancadas = df_history_complecion \\
    # 01. MATEMATICA CRONOLOGICA DE JANELAS TEMPORAIS !
    .withColumn("data_limite", date_add(col("data_evento_compra"), 15)) \\
    .withColumn("idade_estoque_dias", datediff(current_date(), col("data_limite"))) \\
    
    # 02. FLUIDOS REGULARES (Saneamento de Strings Sujos)
    .withColumn("nome_sanificado", trim(upper(col("nome")))) \\
    
    # Extrativistas Severos Baseados em Char Logic (Remove TUDO que for divergente de Letras Normais)
    .withColumn("token_purificado", regexp_replace(col("hash_bruto"), '[^A-Za-z0-9]', '')) \\
    
    # O Pulo Do Gato Fuzzy de Acentos: (Eliminadora global massiva de caracteres graficos).
    .withColumn("string_sem_acento", translate(col("lixo_sujo"), "áàâãäéèêëíìîïóòôõöúùûüç", "aaaaaeeeeiiiiooooouuuuc"))
```
