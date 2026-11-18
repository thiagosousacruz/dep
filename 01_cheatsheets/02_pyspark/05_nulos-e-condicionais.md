# Nulos e Condicionais (PySpark)

> **Aprenda o conceito:** trilha [NULL e lógica de três valores](../../03_trilhas/02_null-e-logica-de-tres-valores.md) — modelo mental, exemplo para prever e erros comuns.

## O que é

Como no SQL, `null` é ausência de valor. Comparações com `null` resultam em `null`, então filtros e joins descartam essas linhas sem aviso. Regras de preenchimento e classificação precisam ser explícitas.

## when / otherwise e coalesce

```python
from pyspark.sql import functions as F

df_classificado = df_vendas.withColumn(
    "tipo_entrega",
    F.when(F.col("prazo_dias") <= 3, "EXPRESSA")
     .when((F.col("prazo_dias") > 3) & (F.col("status") == "PAGA"), "PADRAO_PAGA")
     .otherwise("PADRAO"),
)

df_seguro = df_classificado.withColumn(
    "id_categoria",
    F.coalesce(F.col("id_categoria"), F.lit(-1)),   # chave do membro "desconhecido"
)
```

- Sem `otherwise`, linhas que não atendem nenhuma condição recebem `null`.
- `F.col("a").eqNullSafe(F.col("b"))` compara tratando `null` como igual (equivale a `<=>`).

## dropna, fillna e replace

```python
# Remove linhas com nulo apenas nas colunas exigidas pela regra
antes = df_logistica.count()
df_tratado = df_logistica.dropna(how="any", subset=["idade", "cpf"])
print("removidas:", antes - df_tratado.count())

# Preenche por coluna (o tipo do valor precisa ser compatível com o da coluna)
df_imputado = df_logistica.fillna({"idade": 0, "email": "desconhecido@exemplo.com"})

# Strings "vazias" não são null: normalize antes de tratar nulos
df_normalizado = df_logistica.replace(["N/A", "NA", ""], None, subset=["email", "telefone"])
```

- `dropna` sem `subset` remove a linha por qualquer coluna nula e pode descartar dados válidos.
- `fillna` ignora colunas cujo tipo não combina com o valor informado.
- Preencher com `0` muda médias e somas; registre a regra.

## Divisão por zero

Com ANSI ligado (padrão no Spark 4.x e no serverless), divisão por zero gera erro. Defina a política explicitamente.

```python
df_rentabilidade = df.withColumns({
    "rentabilidade":      F.try_divide("receita", "custo"),    # Spark 3.5+: null se custo = 0
    "rentabilidade_when": F.when(F.col("custo") == 0, None)
                           .otherwise(F.col("receita") / F.col("custo")),
    "is_custo_zero":      (F.col("custo") == 0).cast("int"),   # flag para medir o caso
})
```

## Checklist

- [ ] Toda cadeia `when` tem `otherwise`?
- [ ] Strings vazias e marcadores (`"N/A"`) foram normalizados antes de tratar nulos?
- [ ] Linhas removidas por `dropna` são contadas?
- [ ] Divisões têm política para denominador zero?
