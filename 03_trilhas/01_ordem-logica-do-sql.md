# Ordem lógica do SQL: o que a consulta enxerga em cada cláusula

> **Objetivo:** prever em que momento cada cláusula é avaliada e, com isso, saber onde filtrar, onde um alias existe e por que alguns erros acontecem. **Tempo:** 1 h. **Pré-requisitos:** `SELECT`, `WHERE`, `GROUP BY`.

## O problema

Três erros clássicos de quem está começando têm a mesma causa:

- `WHERE liquido > 100` falha, mesmo com `liquido` definido no `SELECT`;
- `WHERE row_number() OVER (...) = 1` não é aceito;
- um filtro colocado no `HAVING` em vez do `WHERE` muda o número, sem dar erro.

A consulta é **escrita** numa ordem e **avaliada** em outra. Quem conhece a ordem de avaliação para de tentar na sorte.

## Modelo mental

Pense numa linha de montagem. Cada etapa só enxerga o que as anteriores produziram:

```text
1 FROM / JOIN    monta as linhas de origem
2 WHERE          filtra linhas            (ainda não há agregados nem aliases)
3 GROUP BY       forma grupos
4 HAVING         filtra grupos            (agregados já existem)
5 OVER (janela)  calcula janelas sobre o resultado agrupado
6 QUALIFY        filtra pelo resultado da janela (Databricks)
7 SELECT         projeta colunas; aliases nascem aqui
8 DISTINCT       remove duplicatas do que foi projetado
9 ORDER BY       ordena (enxerga aliases)
10 LIMIT         corta
```

- **É uma ordem lógica, não física.** O otimizador pode empurrar filtros para a leitura, mas o *resultado* sempre respeita essa sequência.
- **Janelas rodam depois do `GROUP BY`.** Por isso `SUM(SUM(valor)) OVER ()` é válido: a janela soma os totais por grupo.
- **No PySpark não há ordem de cláusulas:** cada método é uma etapa explícita (`filter` → `groupBy().agg()` → `filter` → `orderBy`). Você escreve a sequência na ordem em que ela acontece.

## Exemplo para prever

```sql
CREATE OR REPLACE TEMP VIEW vendas AS
SELECT * FROM VALUES
  (1, 'A', 100, 'OK'), (2, 'A', 300, 'OK'), (3, 'B', 50, 'CANCELADO'),
  (4, 'B', 700, 'OK'), (5, 'C', 80, 'OK')
AS t(id, loja, valor, status);

-- Consulta 1
SELECT loja, SUM(valor) AS receita
FROM vendas
WHERE status = 'OK'
GROUP BY loja
HAVING SUM(valor) > 200
ORDER BY receita DESC;

-- Consulta 2: mesma coisa, sem o WHERE
SELECT loja, SUM(valor) AS receita
FROM vendas
GROUP BY loja
HAVING SUM(valor) > 200
ORDER BY receita DESC;
```

Anote as linhas de cada uma antes de rodar.

Resultado esperado:

- **Consulta 1:** `B 700`, `A 400`. A venda cancelada sai no `WHERE` (etapa 2), antes de somar; `C` (80) sai no `HAVING` (etapa 4).
- **Consulta 2:** `B 750`, `A 400`. Sem o `WHERE`, os 50 cancelados entram na soma de `B`. Nenhum erro: só um número diferente.

Equivalente em PySpark, já na ordem de avaliação:

```python
from pyspark.sql import functions as F

(spark.table("vendas")
    .filter(F.col("status") == "OK")              # WHERE
    .groupBy("loja").agg(F.sum("valor").alias("receita"))
    .filter(F.col("receita") > 200)               # HAVING
    .orderBy(F.desc("receita")))
```

## Quebre de propósito

1. **Alias no `WHERE`.** `SELECT loja, valor * 0.9 AS liquido FROM vendas WHERE liquido > 100` → erro `UNRESOLVED_COLUMN`: na etapa 2 o alias ainda não existe. Repita a expressão no `WHERE` ou use uma CTE.
2. **Janela no `WHERE`.** `WHERE row_number() OVER (PARTITION BY loja ORDER BY valor DESC) = 1` → erro: janelas são a etapa 5. No Databricks use `QUALIFY`; no Spark open source, calcule a janela numa CTE e filtre fora dela.
3. **`DISTINCT` + `ORDER BY` em coluna não projetada.** `SELECT DISTINCT loja FROM vendas ORDER BY valor` → erro: depois do `DISTINCT` não existe mais um `valor` por linha.
4. **`LIMIT` sem `ORDER BY`.** `SELECT id FROM vendas LIMIT 2` costuma devolver as primeiras linhas lidas, mas **não há garantia de ordem**. Em dados distribuídos o resultado pode mudar entre execuções.
5. **Janela sobre agregado.** `SELECT loja, SUM(valor) AS receita, SUM(SUM(valor)) OVER () AS total FROM vendas GROUP BY loja`. Preveja `total` (1230) e explique por que a janela enxerga as somas, não as linhas originais.

## Erros comuns e como diagnosticar

- **Filtro de linha no `HAVING`** → funciona, mas filtra depois de agregar: é mais caro e às vezes muda o resultado. Regra: condição sem agregado vai no `WHERE`.
- **"Funciona no Databricks e falha no Spark local"** → `QUALIFY` e alguns atalhos são do Databricks. Confira a documentação do runtime.
- **Alias que funciona numa cláusula e não em outra** → aliases existem a partir do `SELECT`. No Spark também valem no `GROUP BY`, no `HAVING`, no `ORDER BY` e dentro do próprio `SELECT` (*lateral alias*), mas nunca no `WHERE`.
- **Top-N com `LIMIT` dando resultado diferente a cada execução** → falta `ORDER BY` com desempate.

## Cheque seu entendimento

1. Por que o alias do `SELECT` não existe no `WHERE`?
2. Em que etapa entram as janelas? E o que isso permite fazer com agregados?
3. Dê uma condição que deve ir no `WHERE` e outra que só pode ir no `HAVING`.
4. Por que `LIMIT` sem `ORDER BY` não serve para "pegar os maiores"?
5. Como filtrar pelo resultado de `row_number()` sem `QUALIFY`?

<details markdown="1">
<summary>Respostas</summary>

1. O `WHERE` é avaliado antes do `SELECT`. Quando ele roda, o alias ainda não foi criado.
2. Depois do `GROUP BY`/`HAVING` e antes do `SELECT`. Por isso a janela enxerga os agregados: `sum(sum(valor)) OVER ()` soma os totais dos grupos.
3. `WHERE status = 'FECHADA'` filtra linhas antes de agrupar; `HAVING sum(valor) > 100` só existe depois do agrupamento.
4. Sem `ORDER BY`, a ordem das linhas não é garantida. O `LIMIT` corta "as primeiras que chegarem", que podem mudar a cada execução.
5. Calcule o `row_number()` numa subconsulta ou CTE e filtre por fora: `SELECT ... FROM (SELECT ..., row_number() OVER (...) AS rn ...) WHERE rn = 1`.

</details>

## Próximos passos

- **Consulta:** [Ordem lógica de avaliação](../01_cheatsheets/01_sql/01_sintaxe-basica.md#ordem-logica-de-avaliacao) · [CTEs para organizar a lógica](../01_cheatsheets/01_sql/05_ctes.md#ctes-para-organizar-a-logica) · [Agregações e filtros por agregação](../01_cheatsheets/01_sql/06_group-by-e-pivots.md#agregacoes-e-filtros-por-agregacao)
- **Prática:** [desafio de ordem lógica](../desafio.html?id=sql-01-ordem-logica) · [desafio de agregações e HAVING](../desafio.html?id=sql-06-agregacoes-filter) · [desafio de CTEs](../desafio.html?id=sql-05-ctes-organizar)
- **Aplicação real:** pegue uma consulta longa autorizada e numere cada cláusula pela ordem de avaliação. Verifique se há filtro de linha no `HAVING` ou `LIMIT` sem `ORDER BY`.
