# Delta Lake API em PySpark

> **Aprenda o conceito:** trilhas [Delta e MERGE idempotente](../../03_trilhas/07_delta-e-merge-idempotente.md) · [Cargas full, incremental e CDC](../../03_trilhas/08_cargas-incrementais-e-cdc.md) — modelo mental, exemplo para prever e erros comuns.

## O que é

`DeltaTable` expõe operações transacionais em Python. SQL continua sendo uma alternativa válida; escolha a interface que deixa a transformação mais clara e testável.

## Merge

```python
from delta.tables import DeltaTable

target = DeltaTable.forName(spark, "gold.vendas")

(
    target.alias("t")
    .merge(
        df_incremental.alias("s"),
        "t.venda_id = s.venda_id",
    )
    .whenMatchedUpdate(
        condition="NOT (t.preco <=> s.preco)",
        set={
            "preco": "s.preco",
            "atualizado_em": "current_timestamp()",
        },
    )
    .whenNotMatchedInsert(
        values={
            "venda_id": "s.venda_id",
            "preco": "s.preco",
            "atualizado_em": "current_timestamp()",
        },
    )
    .execute()
)
```

Garanta que a origem tenha no máximo uma linha por chave de merge e defina uma política de desempate antes da escrita.

## Evolução de schema

```python
(
    df_com_novas_colunas.write
    .format("delta")
    .mode("append")
    .option("mergeSchema", "true")
    .saveAsTable("silver.clientes")
)
```

`mergeSchema` pode adicionar colunas compatíveis, mas não substitui contrato de dados. Valide nomes inesperados, tipos, nulabilidade e impacto nos consumidores. O comportamento exato depende da versão e da operação.

## Restore e vacuum

```python
target.restoreToVersion(42)
target.vacuum(168)
```

Restore depende dos arquivos ainda estarem disponíveis. Vacuum remove arquivos antigos não referenciados e pode invalidar time travel; alinhe retenção com jobs concorrentes e recuperação.

## Otimização e layout

```python
target.optimize().executeCompaction()          # compacta arquivos pequenos

(
    df_vendas.writeTo("main.gold.vendas")
    .clusterBy("dt_venda", "loja_id")          # liquid clustering na criação
    .createOrReplace()
)
```

Em tabelas novas, o Databricks recomenda liquid clustering no lugar de `partitionBy` e `ZORDER` (ver [Delta DML em SQL](../01_sql/10_delta-dml.md)). APIs programáticas de otimização e clustering variam por versão do Delta Lake e do runtime; confirme a compatibilidade antes de usar.

## Checklist

- [ ] A origem é única pela chave de merge?
- [ ] O processamento é idempotente?
- [ ] Evolução de schema é validada, não apenas habilitada?
- [ ] Retenção protege leitores e recuperação?
- [ ] As APIs usadas existem no runtime alvo?

