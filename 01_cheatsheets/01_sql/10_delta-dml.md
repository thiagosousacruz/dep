# Delta Lake: DML e Manutenção

## O que é

Delta Lake adiciona log transacional e controle de concorrência a arquivos de dados. Operações, sintaxe e recursos de otimização podem variar por versão do Delta Lake e pelo Databricks Runtime.

## Merge

A condição do `MERGE` deve identificar no máximo uma linha de origem para cada linha de destino. Deduplique ou rejeite ambiguidades antes da operação.

```sql
MERGE INTO gold.vendas AS target
USING silver.vendas_incrementais AS source
ON target.venda_id = source.venda_id
WHEN MATCHED AND NOT (
  target.preco <=> source.preco
) THEN UPDATE SET
  target.preco = source.preco,
  target.atualizado_em = current_timestamp()
WHEN NOT MATCHED THEN INSERT (
  venda_id, preco, atualizado_em
) VALUES (
  source.venda_id, source.preco, current_timestamp()
);
```

## Time travel e restore

```sql
SELECT * FROM gold.vendas VERSION AS OF 42;
RESTORE TABLE gold.vendas TO VERSION AS OF 42;
```

Time travel depende da disponibilidade do log e dos arquivos referenciados. Um `VACUUM` pode tornar versões antigas ilegíveis.

## Vacuum

```sql
VACUUM gold.vendas RETAIN 168 HOURS;
```

`VACUUM` remove arquivos não referenciados mais antigos que a retenção. Antes de reduzir a retenção padrão, avalie leitores concorrentes, operações longas, políticas de recuperação e requisitos de auditoria. Não trate `VACUUM` como limpeza inofensiva.

## Optimize

```sql
OPTIMIZE gold.vendas;
```

Em Databricks, `OPTIMIZE` compacta arquivos. Estratégias como `ZORDER` dependem dos recursos e recomendações do runtime adotado; escolha colunas a partir dos filtros reais e valide o ganho.

## Checklist

- [ ] A origem do merge é única pela condição usada?
- [ ] O merge é idempotente para reprocessamentos?
- [ ] Retenção e time travel atendem recuperação e auditoria?
- [ ] A otimização física foi medida no padrão real de consultas?
- [ ] A funcionalidade existe na versão do ambiente?

