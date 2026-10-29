# Agrupamentos e Pivots (SQL / Databricks)

## O que é

`GROUP BY` resume linhas em métricas por grupo. `PIVOT` e `UNPIVOT` giram dados entre linhas e colunas. `ROLLUP`, `CUBE` e `GROUPING SETS` produzem subtotais em uma única consulta.

## Agregações e filtros por agregação

Toda coluna não agregada do `SELECT` precisa estar no `GROUP BY`.

```sql
SELECT
    regiao,
    COUNT(*)                                           AS qtd_pedidos,
    SUM(vlr_frete)                                     AS frete_total,
    count_if(status = 'FALHA')                         AS pedidos_falhos,
    SUM(vlr_frete) FILTER (WHERE canal = 'LOJA')       AS frete_loja,
    approx_count_distinct(id_cliente)                  AS clientes_aprox
FROM silver.despachos
GROUP BY regiao
HAVING SUM(vlr_frete) > 100000;
```

- `FILTER (WHERE ...)` e `count_if` evitam `CASE WHEN` dentro de cada agregação.
- `approx_count_distinct` usa HyperLogLog++ com erro relativo padrão de **5%** (`relativeSD = 0.05`); passe um segundo argumento menor para mais precisão (ex.: `approx_count_distinct(id_cliente, 0.01)`), com mais memória. Use quando a contagem exata não for requisito.
- `GROUP BY ALL` (Databricks) agrupa por todas as colunas não agregadas do `SELECT`; prático em exploração, mas explícito é mais seguro em produção.

## PIVOT e UNPIVOT

```sql
-- Linhas → colunas: um valor de ano_fiscal vira uma coluna
SELECT *
FROM (
    SELECT regiao, ano_fiscal, vendas FROM silver.vendas_anuais
)
PIVOT (
    SUM(vendas) FOR ano_fiscal IN (2023, 2024, 2025)
);

-- Colunas → linhas (Spark 3.4+ / Databricks Runtime 12.2+)
SELECT *
FROM bronze.planilha_receita
UNPIVOT (
    receita FOR mes IN (receita_jan AS jan, receita_fev AS fev, receita_mar AS mar)
);
```

- A lista do `PIVOT` é fixa: valores novos não viram colunas automaticamente. Revise-a quando o domínio mudar.
- `UNPIVOT` descarta linhas cujo valor é `NULL`; use `UNPIVOT INCLUDE NULLS` se precisar delas.

## Subtotais: ROLLUP, CUBE e GROUPING SETS

```sql
-- ROLLUP: hierárquico (pais, regiao, estado) → (pais, regiao) → (pais) → total
SELECT pais, regiao, estado, SUM(volume) AS volume,
       grouping_id(pais, regiao, estado) AS nivel
FROM silver.transporte
GROUP BY ROLLUP (pais, regiao, estado);

-- CUBE: todas as combinações das colunas
SELECT ano, tipo_produto, SUM(vendas) AS vendas
FROM silver.faturamento
GROUP BY CUBE (ano, tipo_produto);

-- GROUPING SETS: só as combinações que você listar
SELECT ano, regiao, SUM(vendas) AS vendas
FROM silver.faturamento
GROUP BY GROUPING SETS ((ano, regiao), (ano), ());
```

- Nas linhas de subtotal a coluna agregada aparece como `NULL`. Use `grouping(col)` ou `grouping_id(...)` para distinguir subtotal de um `NULL` real.
- `GROUP BY a, b WITH ROLLUP` é sintaxe equivalente aceita pelo Spark.

## Checklist

- [ ] O grão do resultado está claro (uma linha por quê)?
- [ ] O erro de `approx_count_distinct` é aceitável para o uso?
- [ ] A lista do `PIVOT` cobre os valores atuais do domínio?
- [ ] Linhas de subtotal são identificadas com `grouping`?
