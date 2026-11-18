# Nulos e Condicionais (SQL)

> **Aprenda o conceito:** trilha [NULL e lógica de três valores](../../03_trilhas/02_null-e-logica-de-tres-valores.md) — modelo mental, exemplo para prever e erros comuns.

## O que é

`NULL` representa ausência de valor: não é string vazia (`''`) nem zero. Comparações com `NULL` resultam em `NULL` (desconhecido), o que afeta filtros, joins e agregações de forma silenciosa.

## COALESCE e CASE WHEN

`COALESCE(a, b, ...)` devolve o primeiro argumento não nulo. `CASE WHEN` cobre regras com várias condições — sempre com `ELSE` explícito.

```sql
SELECT
    id_produto,
    COALESCE(nome_produto, 'SEM NOME')  AS nome_produto,
    COALESCE(id_categoria, -1)          AS id_categoria,   -- membro "desconhecido" na dimensão
    CASE
        WHEN status_atual = 'A'                   THEN 'ALTO_RISCO'
        WHEN status_atual = 'M' AND is_ativo      THEN 'MEDIO_RISCO'
        ELSE 'BAIXO_RISCO'
    END AS flag_risco
FROM silver.produtos;
```

- Substituir chave nula por `-1` só funciona se a dimensão tiver a linha `-1 = Desconhecido`; combine isso com o modelo.
- `CASE` avalia as condições em ordem e para na primeira verdadeira.

## NULL em agregações e comparações

```sql
SELECT
    COUNT(*)                 AS linhas,            -- conta todas as linhas
    COUNT(telefone)          AS com_telefone,      -- ignora NULL
    AVG(nota)                AS media_sem_nulos,   -- NULL fica fora do numerador e do denominador
    AVG(COALESCE(nota, 0))   AS media_nulo_zero    -- regra diferente: explicite qual é a correta
FROM envios;
```

- `COUNT(1)` e `COUNT(*)` são equivalentes.
- `WHERE coluna = NULL` nunca é verdadeiro: use `IS NULL` / `IS NOT NULL`.
- Para igualdade que trate `NULL` como igual: `a <=> b` ou `a IS NOT DISTINCT FROM b`.
- Em joins, chaves `NULL` não se correspondem (ver [Joins](07_joins.md)).

## Divisão por zero, NULLIF e funções try_

Com ANSI ligado (padrão no Databricks SQL e no Spark 4.x), dividir por zero gera erro `DIVIDE_BY_ZERO`. Escolha explicitamente o comportamento.

```sql
SELECT
    valor_bruto / NULLIF(comissao, 0)  AS fator,          -- denominador 0 vira NULL
    try_divide(valor_bruto, comissao)  AS fator_try,      -- mesmo efeito, função dedicada
    CASE WHEN comissao IS NULL THEN 1 ELSE 0 END AS is_comissao_ausente   -- flag de qualidade portável
FROM fatos;
```

- `iff(cond, a, b)` existe no Databricks SQL, mas não no Spark open source; `if(cond, a, b)` existe nos dois, mas não é ANSI. `CASE WHEN` é portável.
- Flags de qualidade (`is_*`) permitem medir o problema em vez de escondê-lo.

## Checklist

- [ ] Comparações com nulos usam `IS NULL`, `<=>` ou `IS NOT DISTINCT FROM`?
- [ ] A regra de agregação com nulos (ignorar ou tratar como zero) está explícita?
- [ ] Divisões têm política para denominador zero?
- [ ] Chaves substitutas (`-1`) existem na dimensão?
