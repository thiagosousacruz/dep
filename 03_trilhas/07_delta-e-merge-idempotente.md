# Delta e MERGE idempotente: rodar duas vezes, mesmo resultado

> **Objetivo:** entender o que o log transacional do Delta garante, escolher entre `append`, `overwrite`, `replaceWhere` e `MERGE`, e escrever um `MERGE` que pode ser reexecutado sem estragar a tabela. **Tempo:** 2 h. **Pré-requisitos:** [Grão e cardinalidade](03_grao-e-cardinalidade.md), [Window functions](04_window-functions.md).

## O problema

O job da madrugada falhou no meio e alguém clicou em "repair run". No dia seguinte, a receita de ontem aparece em dobro. Em outro pipeline, o `MERGE` falha toda vez que a origem traz a mesma venda duas vezes. Pipelines **sempre** serão reexecutados: por falha, por reprocessamento ou por correção. A pergunta não é *se*, mas **o que acontece quando isso ocorre**.

## Modelo mental

- **Delta = arquivos Parquet + log transacional (`_delta_log`).** Cada escrita bem-sucedida gera uma **versão** nova de forma atômica: quem lê vê a versão anterior inteira ou a nova inteira, nunca metade. Se o job falhar antes do commit, a tabela continua como estava.
- **Atomicidade não é idempotência.** O Delta garante que *uma* escrita é tudo ou nada. Ele **não** impede que você grave o mesmo lote duas vezes.
- **Idempotente** = rodar o mesmo lote N vezes deixa a tabela igual a rodar uma vez.

```text
Modo de escrita              Reexecutar o mesmo lote   Quando usar
append                       duplica                   eventos imutáveis com controle de lote já processado
overwrite (tabela inteira)   idempotente, caro         tabelas pequenas ou recálculo total
replaceWhere (faixa)         idempotente               reprocessar uma data/partição inteira
MERGE por chave              idempotente se...         upsert por chave de negócio
```

- **O `MERGE` é idempotente se** (1) a origem tem **no máximo uma linha por chave**, (2) a atualização é **condicional** (só quando algo mudou) e (3) os valores gravados vêm **do dado**, não do relógio. Com `current_timestamp()`, cada reexecução grava um valor diferente.

## Exemplo para prever

Rode no Databricks (ou com Delta configurado). Os passos sem `MERGE` também rodam em Spark local.

```sql
CREATE OR REPLACE TABLE alvo (venda_id INT, preco INT, atualizado_em TIMESTAMP);
INSERT INTO alvo VALUES
  (1, 100, TIMESTAMP'2026-11-01 08:00:00'),
  (2, 200, TIMESTAMP'2026-11-01 08:00:00'),
  (3, 300, TIMESTAMP'2026-11-01 08:00:00');

CREATE OR REPLACE TEMP VIEW lote AS
SELECT * FROM VALUES
  (2, 250, TIMESTAMP'2026-11-02 10:00:00'),
  (2, 260, TIMESTAMP'2026-11-02 11:00:00'),   -- mesma venda, extração mais recente
  (3, 300, TIMESTAMP'2026-11-02 10:00:00'),   -- sem mudança
  (4, 400, TIMESTAMP'2026-11-02 10:00:00')    -- venda nova
AS t(venda_id, preco, extraido_em);
```

**Passo 1.** O que acontece com um `MERGE ... ON t.venda_id = s.venda_id` usando `lote` diretamente?

**Passo 2.** Deduplique e faça o `MERGE` condicional:

```sql
CREATE OR REPLACE TEMP VIEW lote_unico AS
SELECT venda_id, preco, extraido_em
FROM (
  SELECT *, row_number() OVER (PARTITION BY venda_id ORDER BY extraido_em DESC) AS rn
  FROM lote
)
WHERE rn = 1;

MERGE INTO alvo AS t
USING lote_unico AS s
ON t.venda_id = s.venda_id
WHEN MATCHED AND NOT (t.preco <=> s.preco) THEN
  UPDATE SET t.preco = s.preco, t.atualizado_em = s.extraido_em
WHEN NOT MATCHED THEN
  INSERT (venda_id, preco, atualizado_em) VALUES (s.venda_id, s.preco, s.extraido_em);

DESCRIBE HISTORY alvo;   -- veja operationMetrics da última versão
```

Quantas linhas são atualizadas e quantas inseridas? E se você rodar o `MERGE` de novo?

Resultado esperado:

- **Passo 1:** erro (`DELTA_MULTIPLE_SOURCE_ROW_MATCHING_TARGET_ROW_IN_MERGE`). Duas linhas de origem disputam a venda 2 e o Delta se recusa a escolher por você.
- **Passo 2:** `lote_unico` fica com `(2, 260)`, `(3, 300)` e `(4, 400)`. O `MERGE` **atualiza 1** (venda 2 → 260), **insere 1** (venda 4), não toca a venda 3 nem a 1. Na tabela final, a venda 1 fica com 100, a 2 com 260, a 3 com 300 e a 4 com 400.
- **Reexecução:** **0 atualizadas e 0 inseridas.** A tabela não muda. Isso é idempotência.

O mesmo em PySpark, com o padrão do cheatsheet:

```python
from delta.tables import DeltaTable
from pyspark.sql import Window, functions as F

w = Window.partitionBy("venda_id").orderBy(F.desc("extraido_em"))
lote_unico = lote.withColumn("rn", F.row_number().over(w)).filter("rn = 1").drop("rn")

(DeltaTable.forName(spark, "alvo").alias("t")
    .merge(lote_unico.alias("s"), "t.venda_id = s.venda_id")
    .whenMatchedUpdate(condition="NOT (t.preco <=> s.preco)",
                       set={"preco": "s.preco", "atualizado_em": "s.extraido_em"})
    .whenNotMatchedInsert(values={"venda_id": "s.venda_id", "preco": "s.preco",
                                  "atualizado_em": "s.extraido_em"})
    .execute())
```

## Quebre de propósito

1. **`append` duas vezes.** `INSERT INTO alvo SELECT venda_id, preco, extraido_em FROM lote_unico` duas vezes e conte por `venda_id`. A duplicação é silenciosa.
2. **Update incondicional.** Tire o `AND NOT (t.preco <=> s.preco)` e rode duas vezes. `DESCRIBE HISTORY` mostra linhas atualizadas *toda vez*: a tabela ganha versões sem mudança real e reescreve arquivos à toa.
3. **Relógio em vez de dado.** Use `t.atualizado_em = current_timestamp()` no update incondicional. Cada reexecução muda a coluna: não é idempotente.
4. **Lote fora de ordem.** Rode o `MERGE` com um lote *antigo* (`extraido_em` de 01/11) depois do novo. Sem a condição `s.extraido_em > t.atualizado_em`, o dado velho sobrescreve o novo.
5. **Volte no tempo.** `SELECT * FROM alvo VERSION AS OF <versão anterior>` e compare. Depois rode `RESTORE TABLE alvo TO VERSION AS OF <versão>` e observe que o restore também vira uma versão nova.

## Erros comuns e como diagnosticar

- **`MERGE` falha com "multiple source rows"** → a origem não é única na chave. Prove com `GROUP BY chave HAVING count(*) > 1` e defina o desempate (mais recente, maior sequência).
- **Valores dobrados depois de reprocessar** → escrita em `append` sem controle de lote. Troque por `MERGE` por chave ou `replaceWhere` na faixa reprocessada.
- **Histórico com versões demais e `MERGE` lento** → update incondicional reescrevendo arquivos. Atualize só quando houver diferença.
- **Dado mais novo sobrescrito por dado mais antigo** → falta a condição de ordem (`s.versao > t.versao`).
- **`VACUUM` "para limpar" e time travel parando de funcionar** → o vacuum remove arquivos de versões antigas. Respeite a retenção.

## Cheque seu entendimento

1. O que o log do Delta garante e o que ele **não** garante?
2. Quais três condições tornam um `MERGE` idempotente?
3. Por que o Delta recusa duas linhas de origem para a mesma linha de destino?
4. Quando `replaceWhere` é melhor que `MERGE`?
5. Como provar, com `DESCRIBE HISTORY`, que uma reexecução não mudou nada?

## Próximos passos

- **Consulta:** [Merge em SQL](../01_cheatsheets/01_sql/10_delta-dml.md#merge) · [Time travel e restore](../01_cheatsheets/01_sql/10_delta-dml.md#time-travel-e-restore) · [Merge no PySpark](../01_cheatsheets/02_pyspark/10_delta-lake-api.md#merge) · [Deduplicação determinística](../01_cheatsheets/02_pyspark/08_window-functions.md#deduplicacao-deterministica)
- **Prática:** [desafio de MERGE em SQL](../desafio.html?id=sql-10-merge) · [desafio de MERGE no PySpark](../desafio.html?id=spk-10-merge) · [time travel](../desafio.html?id=sql-10-time-travel) · [deduplicação](../desafio.html?id=spk-08-dedup-row-number)
- **Aplicação real:** em um pipeline autorizado, simule em ambiente de desenvolvimento a reexecução do mesmo lote. Prove com `DESCRIBE HISTORY` e contagens por chave que nada duplicou. Esse é o critério de avanço da semana 7 do plano.
