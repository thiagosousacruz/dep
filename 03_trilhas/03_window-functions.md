# Window functions: calcular sem perder linhas

> **Objetivo:** escolher entre `GROUP BY` e janela, montar `PARTITION BY` / `ORDER BY` / frame com intenção e prever o efeito de empates. **Tempo:** 1–2 h. **Pré-requisitos:** [Grão e cardinalidade](02_grao-e-cardinalidade.md).

## O problema

Você precisa da última compra de cada cliente, da variação contra o mês anterior ou de um acumulado. Com `GROUP BY` as linhas somem: você fica com uma por grupo e perde o detalhe. Com subconsultas correlacionadas o código fica lento e ilegível. Janelas resolvem, mas três detalhes geram resultados silenciosamente errados: empates, frame padrão e ordenação não determinística.

## Modelo mental

Uma window function responde: **para esta linha, olhando para um grupo de linhas relacionadas, qual é o valor?** O número de linhas não muda.

```text
func(...) OVER (
  PARTITION BY loja          -- quem são meus vizinhos (o grupo)
  ORDER BY dia               -- em que ordem eles estão
  ROWS BETWEEN 2 PRECEDING   -- quais vizinhos entram no cálculo (frame)
       AND CURRENT ROW
)
```

- **Sem `PARTITION BY`**, a tabela inteira é um grupo só — semântica global e, em volume, uma única partição de processamento.
- **Ranking** (`row_number`, `rank`, `dense_rank`) só precisa de ordem; não usa frame.
- **Agregados com `ORDER BY` e sem frame explícito** usam por padrão `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`, que **inclui todos os empates** da linha atual.
- **Ordem determinística:** se o `ORDER BY` tiver empates, `row_number` e `lag` podem mudar entre execuções. Acrescente um desempate (`id`, timestamp).

## Exemplo para prever

```sql
CREATE OR REPLACE TEMP VIEW vendas AS
SELECT * FROM VALUES
  ('A', 1, 10), ('A', 2, 20), ('A', 3, 20), ('B', 1, 5)
AS t(loja, dia, valor);

SELECT loja, dia, valor,
  row_number() OVER (PARTITION BY loja ORDER BY valor DESC) AS rn,
  rank()       OVER (PARTITION BY loja ORDER BY valor DESC) AS rk,
  dense_rank() OVER (PARTITION BY loja ORDER BY valor DESC) AS drk,
  sum(valor)   OVER (PARTITION BY loja ORDER BY valor
                     ROWS  BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS soma_rows,
  sum(valor)   OVER (PARTITION BY loja ORDER BY valor) AS soma_padrao,
  lag(valor)   OVER (PARTITION BY loja ORDER BY dia)   AS valor_anterior
FROM vendas
ORDER BY loja, dia;
```

Preencha a tabela antes de rodar. Resultado esperado:

| loja | dia | valor | rn | rk | drk | soma_rows | soma_padrao | valor_anterior |
|---|---|---|---|---|---|---|---|---|
| A | 1 | 10 | 3 | 3 | 2 | 10 | 10 | null |
| A | 2 | 20 | 1 ou 2 | 1 | 1 | 30 ou 50 | 50 | 10 |
| A | 3 | 20 | 2 ou 1 | 1 | 1 | 50 ou 30 | 50 | 20 |
| B | 1 | 5 | 1 | 1 | 1 | 5 | 5 | null |

- `rank` pula posição depois do empate (1, 1, 3); `dense_rank` não (1, 1, 2).
- Nos dias 2 e 3, `rn` e `soma_rows` são **não determinísticos**: o empate em `valor` não diz quem vem primeiro.
- `soma_padrao` usa `RANGE`: as duas linhas com 20 entram juntas e ambas mostram 50.

## Quebre de propósito

1. **Desempate.** Troque para `ORDER BY valor DESC, dia` e confirme que `rn` e `soma_rows` ficam estáveis.
2. **Remova o `PARTITION BY`** do `rank`. O ranking passa a ser global (B entra na disputa). No plano, aparece um `Exchange SinglePartition`.
3. **Nulos.** Insira `('A', 4, NULL)`. Onde ele cai em `ORDER BY valor DESC`? Teste `NULLS FIRST` e `NULLS LAST`. `sum` ignora nulos; `lag` devolve o nulo como valor anterior.
4. **Parâmetros do `lag`.** Use `lag(valor, 2, 0)` e explique cada argumento.
5. **Média móvel.** Calcule `avg(valor) OVER (PARTITION BY loja ORDER BY dia ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)`. Nas primeiras linhas o frame tem menos de 3 linhas — a média usa só o que existe.

## Erros comuns e como diagnosticar

- **Acumulado "pula" ou repete valores** → frame padrão `RANGE` com empates. Declare `ROWS BETWEEN ...` explicitamente.
- **Deduplicação muda a cada execução** → `row_number` sem desempate. Inclua uma coluna única no `ORDER BY`.
- **Filtrar pelo resultado da janela no `WHERE`** → não é permitido; o `WHERE` roda antes. Use `QUALIFY` (Databricks) ou uma CTE.
- **Job lento ou com spill em janela** → partição lógica muito grande (ou ausente). Verifique a distribuição da chave do `PARTITION BY`.

## Cheque seu entendimento

1. Quando usar janela em vez de `GROUP BY`?
2. Qual é o frame padrão de `sum(...) OVER (ORDER BY x)` e por que ele surpreende com empates?
3. Diferença entre `rank` e `dense_rank` em uma frase.
4. Por que `row_number` precisa de desempate para deduplicar?
5. Por que não dá para usar `row_number()` dentro de `WHERE`?

## Próximos passos

- **Consulta:** [Exemplos em SQL](../01_cheatsheets/01_sql/08_window-functions.md#exemplos) · [Rows versus range](../01_cheatsheets/01_sql/08_window-functions.md#rows-versus-range) · [Deduplicação determinística no PySpark](../01_cheatsheets/02_pyspark/08_window-functions.md#deduplicacao-deterministica) · [Frames e tempo no PySpark](../01_cheatsheets/02_pyspark/08_window-functions.md#frames-e-tempo)
- **Prática:** [ranking, lag e acumulado](../desafio.html?id=sql-08-row-number-lag-acumulado) · [ROWS vs RANGE](../desafio.html?id=sql-08-rows-range) · [deduplicação no PySpark](../desafio.html?id=spk-08-dedup-row-number) · [frames por tempo](../desafio.html?id=spk-08-frames-tempo)
- **Aplicação real:** siga os estágios 4 e 5 do [framework](../framework_dominio_tecnico.html): aplique em uma métrica autorizada (top-3 por categoria, variação MoM) e explique o frame escolhido para alguém do time.
