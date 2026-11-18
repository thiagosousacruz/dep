# Cargas full, incremental e CDC

> **Objetivo:** escolher entre carga full, incremental por watermark e CDC, prever o que cada uma perde ou duplica e montar uma janela de segurança que torne o reprocessamento inofensivo. **Tempo:** 2 h. **Pré-requisitos:** [Delta e MERGE idempotente](07_delta-e-merge-idempotente.md).

## O problema

A carga full da tabela de pedidos levava 5 minutos; um ano depois leva 2 horas. Alguém troca por "pegar só o que mudou desde a última execução". Semanas depois, aparecem pedidos faltando: eram registros que chegaram atrasados. Também há pedidos cancelados que continuam ativos, porque exclusões na origem nunca chegam. Carga incremental é mais barata, mas tem mais jeitos de errar.

## Modelo mental

| Estratégia | Lê da origem | Captura deletes? | Risco principal |
|---|---|---|---|
| Full | tudo, sempre | sim, por ausência | custo cresce com o volume |
| Incremental (watermark) | linhas com coluna de controle acima do último valor | não | atrasados, empate na borda, coluna de controle não confiável |
| CDC | eventos de mudança (I/U/D + sequência) | sim, evento `D` | ordem dos eventos, duplicidade |

- **Watermark** é o maior valor da coluna de controle (`atualizado_em`, `id` crescente) já processado. Fica gravado numa tabela de controle ou num checkpoint.
- **Dados atrasados existem.** Um registro pode ser gravado na origem com `atualizado_em` *anterior* ao último watermark (transação longa, relógio diferente, réplica atrasada).
- **Janela de segurança + MERGE idempotente:** releia um pouco antes do watermark (ex.: 15 min, 1 dia) e aplique com `MERGE`. Reler o que já foi carregado não faz mal; perder um registro, sim.
- **CDC** traz *o que aconteceu* com cada chave. Aplique só o **último evento por chave** (pela sequência) e trate `D` como delete ou soft delete.
- **No Databricks:** *Auto Loader* (`cloudFiles`) controla sozinho quais **arquivos** já foram lidos. *Change Data Feed* expõe as mudanças de uma tabela Delta para as camadas seguintes.

## Exemplo para prever

**Parte 1: watermark.** A última execução carregou até `10:00`. Depois dela, a origem recebeu o registro 4, gravado com horário `09:58` (atrasado).

```sql
CREATE OR REPLACE TEMP VIEW origem AS
SELECT * FROM VALUES
  (1, TIMESTAMP'2026-11-18 09:50:00'),
  (2, TIMESTAMP'2026-11-18 10:00:00'),   -- já carregado na execução anterior
  (3, TIMESTAMP'2026-11-18 10:05:00'),   -- novo
  (4, TIMESTAMP'2026-11-18 09:58:00')    -- novo, mas atrasado
AS t(id, atualizado_em);

-- A
SELECT id FROM origem WHERE atualizado_em >  TIMESTAMP'2026-11-18 10:00:00';
-- B
SELECT id FROM origem WHERE atualizado_em >= TIMESTAMP'2026-11-18 10:00:00';
-- C: janela de segurança de 15 minutos
SELECT id FROM origem WHERE atualizado_em >  TIMESTAMP'2026-11-18 10:00:00' - INTERVAL 15 MINUTES;
```

Resultado esperado:

- **A:** `3`. **Perde o 4** (atrasado). Também perderia um registro gravado exatamente às 10:00 depois da execução anterior.
- **B:** `2, 3`. Relê o 2 (precisa de `MERGE` para não duplicar) e **continua perdendo o 4**.
- **C:** `1, 2, 3, 4`. Relê 1 e 2, mas pega o 4. Com `MERGE` idempotente, as releituras não mudam nada.

**Parte 2: CDC.** Os eventos chegam com operação e sequência:

```sql
CREATE OR REPLACE TEMP VIEW eventos AS
SELECT * FROM VALUES
  (10, 'I', 1, 100), (10, 'U', 2, 120),
  (11, 'I', 3, 50),  (11, 'D', 4, CAST(NULL AS INT)),
  (12, 'I', 5, 70)
AS t(id, op, seq, valor);

CREATE OR REPLACE TEMP VIEW ultimos AS
SELECT id, op, seq, valor
FROM (SELECT *, row_number() OVER (PARTITION BY id ORDER BY seq DESC) AS rn FROM eventos)
WHERE rn = 1;
```

Com o destino vazio, que linhas ficam no final? Resposta: `10 → 120` e `12 → 70`. O 11 foi inserido e excluído no mesmo lote, então não entra. Aplicação no Delta:

```sql
MERGE INTO alvo AS t
USING ultimos AS s
ON t.id = s.id
WHEN MATCHED AND s.op = 'D' THEN DELETE
WHEN MATCHED AND s.seq > t.seq THEN UPDATE SET t.valor = s.valor, t.seq = s.seq
WHEN NOT MATCHED AND s.op <> 'D' THEN INSERT (id, valor, seq) VALUES (s.id, s.valor, s.seq);
```

**Parte 3: arquivos com Auto Loader** (só no Databricks). O checkpoint guarda quais arquivos já foram processados. `availableNow` processa o que há de novo e encerra, como um job batch:

```python
(spark.readStream.format("cloudFiles")
    .option("cloudFiles.format", "json")
    .option("cloudFiles.schemaLocation", caminho_checkpoint)
    .load(caminho_origem)
  .writeStream
    .option("checkpointLocation", caminho_checkpoint)
    .trigger(availableNow=True)
    .toTable("bronze.eventos"))
```

## Quebre de propósito

1. **Empate na borda.** Acrescente um registro `5` com horário `10:00:00`, gravado *depois* da execução anterior. Com `>`, ele é perdido para sempre. Por isso a janela de segurança é mais robusta que escolher entre `>` e `>=`.
2. **Delete invisível.** Remova o registro 1 da origem e rode a consulta C. Nada indica a exclusão. Sem CDC, deletes só são detectados por comparação full (anti join entre origem e destino) de tempos em tempos.
3. **Eventos fora de ordem.** No `MERGE` de CDC, tire a condição `s.seq > t.seq` e aplique primeiro um lote novo e depois um lote antigo. O valor antigo volta.
4. **Coluna de controle não confiável.** Imagine um sistema que atualiza registros sem mudar `atualizado_em`. Qual estratégia ainda funciona? (Só full ou CDC.)
5. **Checkpoint apagado.** No Auto Loader, apagar o checkpoint faz todos os arquivos serem lidos de novo. Com `append` no bronze, isso duplica tudo. O que precisa estar idempotente a jusante?

## Erros comuns e como diagnosticar

- **Registros faltando "aleatoriamente"** → dados atrasados ou empate na borda do watermark. Compare contagens por dia entre origem e destino e use janela de segurança.
- **Cancelamentos que não aparecem** → incremental por watermark não captura deletes. Use CDC, soft delete na origem ou reconciliação full periódica.
- **Watermark avançado com a carga falhando** → atualize o watermark **só depois** do commit da escrita.
- **Watermark calculado pelo relógio do job** → use o **maior valor lido da origem**, não `current_timestamp()`. Relógios diferem.
- **CDC aplicado evento a evento num loop** → lento e sujeito a ordem errada. Reduza para o último evento por chave e aplique um `MERGE` por lote.

## Cheque seu entendimento

1. Por que `>` e `>=` no watermark não resolvem os dados atrasados?
2. Por que reler dados com janela de segurança é seguro, e qual a pré-condição?
3. O que a carga incremental por watermark não consegue capturar?
4. Por que aplicar só o último evento por chave em CDC?
5. Quando atualizar o watermark: antes ou depois da escrita? Por quê?

<details markdown="1">
<summary>Respostas</summary>

1. Os dois só olham para frente. Um registro atrasado chega com horário **anterior** ao watermark e fica de fora nos dois casos; o `>=` só resolve o empate exato na borda.
2. Porque o que foi relido é aplicado com `MERGE` idempotente e não muda nada. A pré-condição é justamente essa: escrita idempotente por chave, nunca `append`.
3. Deletes (a linha some da origem e não há o que ler) e registros cuja coluna de controle não é atualizada nas mudanças.
4. Só o último evento representa o estado atual. Aplicar todos os eventos de uma vez gera várias linhas de origem para a mesma chave (o `MERGE` falha) ou um resultado que depende da ordem.
5. Depois do commit da escrita. Se avançar antes e a carga falhar, os registros daquele intervalo nunca mais serão lidos.

</details>

## Próximos passos

- **Consulta:** [Merge em SQL](../01_cheatsheets/01_sql/10_delta-dml.md#merge) · [Leitura de arquivos com schema explícito](../01_cheatsheets/02_pyspark/02_leitura-escrita-io.md#arquivos-com-schema-explicito) · [Colunas técnicas úteis no medalhão](../01_cheatsheets/02_pyspark/14_medallion-architecture.md#4-colunas-tecnicas-uteis)
- **Prática:** [MERGE em SQL](../desafio.html?id=sql-10-merge) · [colunas técnicas](../desafio.html?id=spk-14-colunas-tecnicas) · [perda de linhas em joins (reconciliação)](../desafio.html?id=spk-12-perda-join)
- **Aplicação real:** para uma ingestão autorizada, escreva qual é a estratégia (full, watermark ou CDC), a coluna de controle, onde o watermark fica gravado, a janela de segurança e como deletes são tratados. É a base do critério de avanço das semanas 9–10 do plano.
