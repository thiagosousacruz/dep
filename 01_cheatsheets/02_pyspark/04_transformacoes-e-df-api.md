# Transformações e DataFrame API (PySpark)

## O que é

As operações do dia a dia: projetar, criar e renomear colunas, filtrar, deduplicar, ordenar, empilhar e limpar textos e datas. DataFrames são imutáveis: cada operação devolve um novo DataFrame, então o código é escrito como uma cadeia de métodos.

## Projeção, novas colunas e renomeação

```python
from pyspark.sql import functions as F

df_clientes = (
    df_base
    .select("cliente_id", "nome", "celular", "faturamento")
    .withColumn("sistema_origem", F.lit("CRM_V1"))           # literal constante
    .withColumnsRenamed({"cliente_id": "id_cliente"})        # Spark 3.4+
    .drop("celular")
)

# Várias colunas de uma vez (Spark 3.3+): um único passo no plano
df_clientes = df_clientes.withColumns({
    "nome": F.trim(F.upper("nome")),
    "faixa": F.when(F.col("faturamento") > 1000, "ALTA").otherwise("BAIXA"),
})

# Expressões SQL em texto
df_sel = df_bruto.selectExpr("id_pk AS id", "CAST(faturamento AS INT) AS faturamento")
```

- Muitos `withColumn` em loop deixam o plano lento para analisar; prefira `withColumns` ou um único `select`.

## Filtros

Em PySpark, `&` (e), `|` (ou) e `~` (não) têm precedência maior que comparações: **cada condição precisa de parênteses**. Agrupe também a mistura de `&` e `|` para deixar a regra explícita.

```python
df_filtrado = df_clientes.filter(
    (F.col("nome").isNotNull() & (F.col("celular") != ""))
    | F.col("status").isin("VIP", "GOLD")
)

df_sem_banidos = df_filtrado.filter(~F.col("status").isin("BANIDO"))
```

- `and`/`or` do Python não funcionam com colunas; use `&`/`|`.

## Deduplicação

`dropDuplicates(cols)` mantém **uma linha qualquer** por chave. Ordenar antes com `orderBy` **não garante** qual linha fica. Quando a regra é "a mais recente", use janela com desempate.

```python
from pyspark.sql.window import Window

# Qualquer linha por chave (quando as duplicatas são idênticas)
df_unico = df.dropDuplicates(["id_pk", "documento"])

# A linha mais recente por chave, de forma determinística
ultima = Window.partitionBy("id_pk").orderBy(F.col("atualizado_em").desc(), F.col("versao").desc())
df_recente = (
    df.withColumn("rn", F.row_number().over(ultima))
      .filter("rn = 1")
      .drop("rn")
)
```

- `orderBy` global faz shuffle e ordenação de tudo; use só quando a ordem do resultado importa.

## Empilhamento e amostragem

```python
# Empilha pelo NOME das colunas; colunas ausentes viram NULL
df_historico = df_janeiro.unionByName(df_fevereiro, allowMissingColumns=True)

# Amostra aproximada de 1% (o tamanho exato varia)
df_amostra = df_historico.sample(withReplacement=False, fraction=0.01, seed=42)
```

- `union` empilha por **posição** e não remove duplicatas; prefira `unionByName`.

## Textos e datas com funções nativas

Funções nativas rodam na JVM/Photon e são visíveis ao otimizador; UDFs Python para a mesma tarefa são mais lentas.

```python
df_limpo = df_historico.withColumns({
    "data_limite":       F.date_add("data_compra", 15),
    "dias_desde_limite": F.datediff(F.current_date(), F.date_add("data_compra", 15)),
    "nome_padrao":       F.trim(F.upper("nome")),
    "token":             F.regexp_replace("hash_bruto", r"[^A-Za-z0-9]", ""),
    "nome_sem_acento":   F.translate("nome", "áàâãäéèêëíìîïóòôõöúùûüç", "aaaaaeeeeiiiiooooouuuuc"),
})
```

- Em Python, use string raw (`r"..."`) para regex e evitar escapes duplos.

## Checklist

- [ ] Cada condição de filtro está entre parênteses?
- [ ] A deduplicação tem regra determinística quando a linha escolhida importa?
- [ ] Uniões usam `unionByName`?
- [ ] Funções nativas foram usadas antes de UDFs?
