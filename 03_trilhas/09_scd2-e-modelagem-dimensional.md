# SCD2 e modelagem dimensional: o passado não pode mudar sozinho

> **Objetivo:** separar fato e dimensão pelo grão, decidir quando um atributo precisa de histórico, implementar SCD tipo 2 com `MERGE` e cruzar a fato com a versão vigente na data do evento. **Tempo:** 2–3 h. **Pré-requisitos:** [Grão e cardinalidade](03_grao-e-cardinalidade.md), [Delta e MERGE idempotente](07_delta-e-merge-idempotente.md).

## O problema

Em junho, o cliente C1 passou do segmento Bronze para Ouro. No relatório de receita por segmento, a venda de março de C1 agora aparece como Ouro, e o número de Bronze do primeiro trimestre caiu, sem ninguém ter mexido nas vendas. A dimensão foi sobrescrita (SCD tipo 1) e o passado mudou de significado. Em outro relatório, alguém guardou o histórico, mas cruzou sem filtro de vigência, e a receita **dobrou**.

## Modelo mental

- **Fato** = eventos e medidas, com grão claro (uma linha por venda, por item, por dia/loja). **Dimensão** = contexto descritivo (cliente, produto, loja, calendário).
- **SCD é a decisão de como uma dimensão muda:**

| Tipo | O que faz | Use quando |
|---|---|---|
| 1 | sobrescreve | correção ou atributo sem valor histórico |
| 2 | fecha a versão antiga e cria uma nova | o atributo muda a interpretação do passado (segmento, região, categoria) |
| 3 | guarda "valor anterior" numa coluna | histórico curto e controlado |

- **SCD2 em uma linha:** cada versão tem `inicio_vigencia`, `fim_vigencia` (exclusivo, nulo na versão atual), a flag `atual` e uma **surrogate key** (`sk`) própria. A chave de negócio (`cliente_id`) se repete; a `sk` não.
- **Invariantes que você deve testar:** no máximo uma versão atual por chave de negócio; vigências sem sobreposição; nenhuma lacuna entre versões.
- **A fato encontra a versão certa** de duas formas: (a) grava a `sk` vigente no momento da carga, ou (b) faz um join por intervalo: `data_evento >= inicio AND data_evento < fim`.

## Exemplo para prever

```sql
-- Dimensão atual (antes da carga de 01/06)
CREATE OR REPLACE TABLE dim_cliente (
  sk BIGINT GENERATED ALWAYS AS IDENTITY,
  cliente_id STRING, segmento STRING,
  inicio_vigencia DATE, fim_vigencia DATE, atual BOOLEAN
);
INSERT INTO dim_cliente (cliente_id, segmento, inicio_vigencia, fim_vigencia, atual) VALUES
  ('C1', 'Bronze', DATE'2026-01-01', NULL, true),
  ('C2', 'Prata',  DATE'2026-01-01', NULL, true);

-- Snapshot da origem em 01/06
CREATE OR REPLACE TEMP VIEW stage AS
SELECT * FROM VALUES
  ('C1', 'Ouro',   DATE'2026-06-01'),   -- mudou
  ('C2', 'Prata',  DATE'2026-06-01'),   -- igual
  ('C3', 'Bronze', DATE'2026-06-01')    -- novo
AS t(cliente_id, segmento, data_ref);
```

O `MERGE` do SCD2 precisa fazer duas coisas com C1: **fechar** a versão Bronze e **inserir** a versão Ouro. Um `MERGE` só toca cada linha de destino uma vez, então a origem é montada com cada mudança **duas vezes**: uma com a chave (para casar e fechar) e outra com `merge_key` nulo (para nunca casar e ser inserida).

```sql
MERGE INTO dim_cliente AS t
USING (
  SELECT s.cliente_id AS merge_key, s.* FROM stage s
  UNION ALL
  SELECT CAST(NULL AS STRING) AS merge_key, s.* FROM stage s
  JOIN dim_cliente d ON s.cliente_id = d.cliente_id AND d.atual
  WHERE NOT (s.segmento <=> d.segmento)
) AS s
ON t.cliente_id = s.merge_key AND t.atual
WHEN MATCHED AND NOT (t.segmento <=> s.segmento) THEN
  UPDATE SET t.atual = false, t.fim_vigencia = s.data_ref
WHEN NOT MATCHED THEN
  INSERT (cliente_id, segmento, inicio_vigencia, fim_vigencia, atual)
  VALUES (s.cliente_id, s.segmento, s.data_ref, NULL, true);
```

Antes de rodar: quantas linhas a origem do `MERGE` tem? Quantas versões são fechadas e quantas inseridas? Quantas linhas tem a dimensão no final?

Resultado esperado:

- **Origem:** 4 linhas: C1 com chave, C1 com `merge_key` nulo, C2 e C3.
- **Fechada:** 1 (C1 Bronze, `fim_vigencia = 2026-06-01`). **Inseridas:** 2 (C1 Ouro e C3 Bronze). C2 não muda.
- **Dimensão final:** 4 linhas, uma atual por cliente.
- **Reexecução com o mesmo `stage`:** nada muda. C1 atual já é Ouro e C3 já existe.

Agora a fato:

```sql
CREATE OR REPLACE TEMP VIEW vendas AS
SELECT * FROM VALUES
  ('C1', DATE'2026-03-10', 100), ('C1', DATE'2026-07-02', 200), ('C2', DATE'2026-07-02', 50)
AS t(cliente_id, data_venda, valor);

SELECT d.segmento, sum(v.valor) AS receita
FROM vendas v
JOIN dim_cliente d
  ON  v.cliente_id = d.cliente_id
  AND v.data_venda >= d.inicio_vigencia
  AND v.data_venda <  coalesce(d.fim_vigencia, DATE'9999-12-31')
GROUP BY d.segmento;
```

Resultado: **Bronze 100, Ouro 200, Prata 50.** A venda de março continua Bronze.

## Quebre de propósito

1. **Só a versão atual.** Troque a condição de vigência por `AND d.atual`. Resultado: Ouro 300, Prata 50. A história foi reescrita (é o mesmo efeito de um SCD1).
2. **Sem filtro nenhum.** Cruze só por `cliente_id`. São 5 linhas e receita 650, contra 350 reais: um exploding join causado pelas duas versões de C1.
3. **Fim inclusivo.** Use `<=` no fim da vigência e crie uma venda de C1 em `2026-06-01`. Ela casa com as duas versões. Por isso o fim é **exclusivo**.
4. **Teste as invariantes.** `SELECT cliente_id FROM dim_cliente WHERE atual GROUP BY cliente_id HAVING count(*) > 1` precisa voltar vazio. Depois, rode o `MERGE` com duas linhas de C1 no `stage` e veja o que acontece.
5. **Atributo que muda demais.** Imagine "saldo de pontos" como SCD2: uma versão por dia por cliente. Quando esse atributo deveria ir para a fato (ou para um snapshot) em vez da dimensão?

## Erros comuns e como diagnosticar

- **Relatório do passado muda depois de uma carga** → dimensão em SCD1 para um atributo histórico, ou join usando `atual`. Revise a decisão por atributo.
- **Receita dobrada ao cruzar com dimensão histórica** → join sem vigência. Compare `count(*)` antes e depois do join (lição de grão).
- **Duas versões atuais para o mesmo cliente** → origem duplicada no `stage` ou `MERGE` interrompido sem transação. Teste a invariante depois de cada carga.
- **Vigências sobrepostas ou com buracos** → `fim_vigencia` calculado com regra diferente de `inicio_vigencia`. Use a mesma data de referência para fechar uma versão e abrir a seguinte.
- **Fato com `sk` errada em reprocessamentos** → se a fato grava a `sk`, o reprocessamento precisa buscar a versão vigente **na data do evento**, não a atual.

## Cheque seu entendimento

1. Qual a diferença entre chave de negócio e surrogate key, e por que o SCD2 precisa da segunda?
2. Por que o `MERGE` do SCD2 recebe cada mudança duas vezes?
3. Quais três invariantes uma dimensão SCD2 deve respeitar?
4. Por que o fim da vigência deve ser exclusivo?
5. Quando um atributo deveria ser tipo 1 e não tipo 2?

<details markdown="1">
<summary>Respostas</summary>

1. A chave de negócio identifica a entidade (o cliente) e se repete entre versões. A surrogate key identifica **cada versão** e não se repete, e é ela que a fato usa para apontar a versão certa.
2. Uma vez com a chave preenchida, para casar com a versão atual e fechá-la; outra com a chave de merge nula, que não casa com nada e por isso **insere** a versão nova.
3. No máximo uma versão atual por chave de negócio; vigências sem sobreposição; nenhuma lacuna entre versões.
4. Para um instante cair em exatamente uma versão. Com o fim inclusivo, o dia da troca casa com duas versões e o join duplica a fato.
5. Quando é correção de erro ou o atributo não muda a interpretação do passado (por exemplo, um telefone ou a grafia de um nome). Historizar isso só infla a dimensão.

</details>

## Próximos passos

- **Consulta:** [SCDs (complementar)](../01_cheatsheets/03_modeling-e-analytics/03_slowly-changing-dimensions.md) · [Modelagem dimensional (complementar)](../01_cheatsheets/03_modeling-e-analytics/01_modelagem-dimensional.md) · [Tipos de fato (complementar)](../01_cheatsheets/03_modeling-e-analytics/02_tipos-tabelas-fato.md) · [Merge em SQL](../01_cheatsheets/01_sql/10_delta-dml.md#merge)
- **Prática:** [MERGE em SQL](../desafio.html?id=sql-10-merge) · [unicidade do grão](../desafio.html?id=sql-11-grao-unicidade) · [cardinalidade](../desafio.html?id=sql-07-cardinalidade) · [granularidade no medalhão](../desafio.html?id=spk-14-granularidade)
- **Aplicação real:** em uma dimensão autorizada, liste os atributos e classifique cada um como tipo 1 ou 2, com justificativa. Escreva o teste de "uma versão atual por chave". É o "SCD Type 2 do zero" do mês 9 do plano de 12 meses.
