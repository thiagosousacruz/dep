# Sintaxe Básica (SQL / Databricks)

> **Aprenda o conceito:** trilha [Ordem lógica do SQL](../../03_trilhas/01_ordem-logica-do-sql.md) — modelo mental, exemplo para prever e erros comuns.

## O que é

A estrutura de uma consulta `SELECT` e a ordem lógica em que suas cláusulas são avaliadas. Entender essa ordem explica por que um alias do `SELECT` não pode ser usado no `WHERE`, por que agregados são filtrados no `HAVING` e onde entra o `QUALIFY`.

## Ordem lógica de avaliação

A ordem em que escrevemos não é a ordem em que a consulta é avaliada. A ordem lógica é:

`FROM/JOIN → WHERE → GROUP BY → HAVING → janelas (OVER) → QUALIFY → SELECT (projeção) → DISTINCT → ORDER BY → LIMIT`

O otimizador pode reordenar a execução física (por exemplo, empurrar filtros para a leitura), mas o resultado sempre respeita essa ordem lógica.

```sql
SELECT
    categoria_id,
    SUM(valor) AS receita              -- projeção: aliases nascem aqui
FROM vendas                            -- 1. origem
WHERE status_venda = 'FECHADA'         -- 2. filtra linhas antes de agregar
GROUP BY categoria_id                  -- 3. agrupa
HAVING SUM(valor) > 1000               -- 4. filtra grupos (resultado de agregados)
ORDER BY receita DESC                  -- ORDER BY já enxerga aliases do SELECT
LIMIT 10;
```

- Filtre no `WHERE` o que não depende de agregação: reduz o volume antes do `GROUP BY`.
- Use `HAVING` apenas para condições sobre agregados.
- `QUALIFY` filtra o resultado de funções de janela (ver [Window functions](08_window-functions.md)). É suportado no Databricks, mas não no Spark open source; fora do Databricks, use uma subconsulta com filtro sobre a coluna da janela.

## Filtros: IN, BETWEEN e LIKE

```sql
SELECT *
FROM clientes
WHERE sigla_estado IN ('SP', 'RJ', 'MG')                  -- lista de valores
  AND data_nascimento BETWEEN DATE '2000-01-01'
                          AND DATE '2000-01-05'           -- inclui as duas bordas
  AND nome_cliente ILIKE 'thiago%'                        -- ILIKE: sem diferenciar maiúsculas
  AND status_conta NOT IN ('CANCELADO', 'BLOQUEADO');
```

- `LIKE` diferencia maiúsculas de minúsculas; `ILIKE` não (Databricks SQL / Spark 3.3+).
- `BETWEEN` em coluna `TIMESTAMP` com limite `DATE` corta o último dia em `00:00:00`. Para intervalos de tempo prefira `ts >= início AND ts < fim_exclusivo`.
- `NOT IN` com subconsulta que retorna `NULL` não devolve nenhuma linha. Use `NOT EXISTS` ou `LEFT ANTI JOIN` (ver [Joins](07_joins.md)).

```sql
-- Retorna zero linhas se algum id_cliente em bloqueados for NULL
SELECT * FROM clientes WHERE id_cliente NOT IN (SELECT id_cliente FROM bloqueados);

-- Seguro com NULL
SELECT * FROM clientes c
WHERE NOT EXISTS (SELECT 1 FROM bloqueados b WHERE b.id_cliente = c.id_cliente);
```

## DISTINCT com propósito

`DISTINCT` força agrupamento por todas as colunas projetadas e, em geral, um shuffle. Usá-lo para "corrigir" duplicidade esconde a causa (normalmente um join que multiplicou linhas).

```sql
-- Evite: deduplica tudo sem explicar de onde veio a duplicidade
SELECT DISTINCT * FROM fato_vendas;

-- Prefira: distinct sobre a chave que você realmente precisa
SELECT DISTINCT id_cliente
FROM clientes_ativos
WHERE id_cliente IS NOT NULL;
```

Se a duplicidade é inesperada, investigue a cardinalidade antes de deduplicar.

## Operadores de conjunto

Combinam resultados de consultas com o mesmo número de colunas e tipos compatíveis. A correspondência é por **posição**, não por nome.

```sql
-- UNION ALL: empilha mantendo duplicatas (sem custo de deduplicação)
SELECT id_user FROM base_antiga
UNION ALL
SELECT id_user FROM base_nova;

-- UNION: empilha e remove duplicatas (equivale a UNION DISTINCT)
SELECT id_user FROM base_antiga
UNION
SELECT id_user FROM base_nova;

-- EXCEPT: o que está em A e não está em B (distinct; MINUS é sinônimo)
SELECT id_transacao FROM extrato_banco
EXCEPT
SELECT id_transacao FROM base_conciliada;

-- INTERSECT: o que existe nos dois lados
SELECT id_produto FROM catalogo_site
INTERSECT
SELECT id_produto FROM estoque_fisico;
```

- `EXCEPT ALL` e `INTERSECT ALL` preservam multiplicidade — úteis para comparar tabelas linha a linha em migrações.
- Ao contrário de `=`, operadores de conjunto tratam `NULL` como igual a `NULL`.

## Checklist

- [ ] Filtros de linha estão no `WHERE` e filtros de agregado no `HAVING`?
- [ ] Intervalos de tempo usam limite superior exclusivo?
- [ ] `NOT IN` com subconsulta foi substituído por `NOT EXISTS` quando há risco de `NULL`?
- [ ] `DISTINCT` tem justificativa de negócio e não mascara um join errado?
