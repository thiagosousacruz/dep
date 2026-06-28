# Exploracao e Tipagem (PySpark)

## O que e
As chaves bases que revelam o estado fisíco estrutural após e ingestao crua no notebook (`Exploratão Visual`), e o cast de almejamentos obrigatórios de engrenagem (`Tipagem Forte/Timezones`). O casting robusto e preventor fatal contra truncamento de inteiros cruzando strings!

## Nivel Junior/Pleno: Inspeções Rapidas e Describe
Técnicas interativas na UI para confirmar a volumetria provisória e esquemas ocultos.

```python
# 1. ESQUELETIZACAO DA ARVORE (Mapeia chaves, structs imbuidas em json, arrey types e dicts internos e os expoe em ramificacao hierarquica estrutural).
df_recebido.printSchema()

# 2. PROFILING DE MAX/MIN NUMERICS (Estatistica basica sobre fatias inteiras pulando strings)
df_recebido.select("idade", "faturamento").describe().show()

# 3. INTEROPERABILIDADES DE TELA DE DEVS
display(df_recebido) # No databricks workspace rederiza nativo tabelado front-end.
```

## Nivel Pleno: Casting Tipografico Explicito
Evitar o truncamento silencioso garantindo compatibilidade estática em joins ou writes.

```python
from pyspark.sql.functions import col
from pyspark.sql.types import IntegerType, DecimalType

df_formatado = df_origem \\
    .withColumn("id_int_base", col("id").cast(IntegerType())) \\
    
    # Casting monetario com delimitador obrigatorio (Tamanho Bytes, Restos Centesimal).
    .withColumn("vlr_moeda", col("faturamento").cast(DecimalType(18,2))) \\
    
    # Cast condicional boleano automático a vera. Produze True/False limpo in-loop.
    .withColumn("indicador_alta_compra", (col("faturamento") > 1500.0))
```

## Nivel Senior: Timestamps e Correcoes de Fuso-Horario (TimeZone Adjustments)
O pesadelo global das clouds. Um Log ERP Brasileiro gerado em sua data Local crua na origem é hospedado no Azure em DataCenters americanos rodando a engine no UTC+0 nativo. Cruzações temporais e YTD quebram se expostos no Pyspark.

```python
from pyspark.sql.functions import to_timestamp, to_date, current_timestamp, from_utc_timestamp

# Timezone de sessoes default: current_timestamp reflete o relogio matriz host da Sessão.

df_cronos = df_fatos_logs \\
    # PARSING MASCARADO: Formataçoes exóticas stringadas para Date oficial. (O 'MM' minúsculo difere do sql)
    .withColumn(
        "dt_nascimento_limpa", 
        to_date(col("dt_bruta_erada"), 'dd/MM/yyyy') 
    ) \\
    # TIMEZONE OFFSETTING BINDED (Geralmente salva Painel analitico trazendo do utc pro local regional):
    .withColumn(
        "ts_visita_hora_brasil", 
        from_utc_timestamp(col("ts_evento_utc"), 'America/Sao_Paulo')
    )
```
