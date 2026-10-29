# Estruturas Complexas JSON e Schema Enforcement (PySpark)

## O que e
Dados semiestruturados exigem distinguir texto JSON de colunas `struct` e `array` já tipadas. Um schema explícito torna o contrato observável; registros incompatíveis ainda precisam de validação e tratamento.

## Nivel Junior/Pleno: A Extracao Logica Simples (Struct Dot Notation)
Extrativismo cirurgico quando as origens do Json ja foram blindadas por padrao.

```python
from pyspark.sql.functions import col, get_json_object, explode, split

# ESTRUTURA BLINDADA EMBARCADA
# Para uma coluna struct já tipada, projete os campos necessários.
df_tratar = df_ingestao.select(
    "id_registro",
    # Mapeamentos Ocultos usando a Dot Notation Extrativista da arvore:
    col("Metadata_Sistema.rede_configuracoes.versao_ssl_https").alias("Protocolo")
)

# O TEXTO JSON CRU / SUJO 
# Stringify cru vindo da Bronze sem tipos nativos. Vc precisa da funçao nativa JSON!
df_strings = df_sujo_bronze.withColumn(
    "versao_textual_achada",
    get_json_object("logs_campo_txt", "$.payloadRoot.identificadores[0].idCore") 
)
```

## O Gerador Explode: Acelerador Dimensional (Flatenning Arrays)
Multiplicacao Plana de Listas. Transformar 1 Recibo (`["Livro", "Caneta"]`) em 2 Fatos Isoladas sem ferir dependencias operantes. 

```python
# ARRAY FLATENNING NATIVO (Transformado pra matriz de lista string delimitada)
df_geracao = df_receita_bruta \\
    .withColumn("vetor_lista_nativa", split(col("tags_texto_unidas"), ",")) \\
    .withColumn("Registro_Fisico_Para_Cada_Item", explode(col("vetor_lista_nativa")))
# Acaba de se desdobrar a linha antiga unificada multiplicando verticalmente os limites array p calculo singular!
```

## Nivel Sênior: Schema Enforcement na Entrada Tipada
Defina tipos e nulabilidade esperados, depois meça registros incompatíveis. Informar um schema na leitura não garante sozinho que todos os valores atendem às regras de negócio.

```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from pyspark.sql.functions import from_json, schema_of_json, lit

# CONTRATO BASE OBRIGATORIO:
schema_oficial_vendas = StructType([
    StructField("id_venda", StringType(), nullable=False),  
    StructField("valor_lote", IntegerType(), nullable=True) 
])
# O schema orienta o parser; valide campos nulos ou registros corrompidos após a leitura.
df_fixo = spark.read.schema(schema_oficial_vendas).json("/mnt/bronze/*.json")

# 2. INFERENCIA DINÂMICA ENVOLVENDO SCHEMAS STRINGS MISTURADOS
# Seu DataFrame leu com sucesso da bronze mas os Campos estao inteiros Textos Stringificados em 1 unica Coluna (Raw).
schema_dinamico = schema_of_json(lit('{"nome": "ex", "idade": 10, "isTrue": false}'))

df_tabelado_nativo = df_bronze_bruto.withColumn(
    "json_estruturado_com_tipo_dinamico", 
    from_json(col("LogStringCompletaUnica"), schema_dinamico)
)

# SEÇÕES DE FALLBACK (COLUNAS FALTANTES NOS STRUCTS)
# Alguns JSONS diarios podem apagar colunas temporarias. Previna Joins q busquem strings estritas reescrevendo preenchimentos.
lista_fields_mandatoria = ["id", "nome", "opcional_extinta"]
for campo in lista_fields_mandatoria:
    if campo not in df_tabelado_nativo.columns:
        df_tabelado_nativo = df_tabelado_nativo.withColumn(campo, lit(None))
```
