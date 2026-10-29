# SQL Joins (Databricks / Spark SQL)

## O que é

Joins combinam conjuntos de dados por uma condição. Em Spark, podem exigir shuffle; o custo depende do volume, da distribuição das chaves, da estratégia física e das colunas transportadas.

## Quando usar

```sql
-- INNER: somente correspondências
SELECT f.id_venda, d.uf
FROM fato_vendas AS f
INNER JOIN dim_loja AS d ON f.loja_id = d.loja_id;

-- LEFT: preserva todas as linhas da esquerda
SELECT f.id_venda, d.uf
FROM fato_vendas AS f
LEFT JOIN dim_loja AS d ON f.loja_id = d.loja_id;

-- FULL OUTER: útil para reconciliação
SELECT coalesce(a.id, b.id) AS id, a.valor, b.valor
FROM origem AS a
FULL OUTER JOIN destino AS b ON a.id = b.id;

-- CROSS: produto cartesiano intencional
SELECT c.data, f.faixa
FROM calendario AS c
CROSS JOIN faixas AS f;
```

`LEFT SEMI JOIN` retorna linhas da esquerda com correspondência; `LEFT ANTI JOIN`, as linhas sem correspondência. Ambos evitam carregar colunas do lado direito.

```sql
SELECT a.id FROM clientes AS a LEFT SEMI JOIN acessos AS b ON a.id = b.cliente_id;
SELECT a.id FROM clientes AS a LEFT ANTI JOIN acessos AS b ON a.id = b.cliente_id;
```

## Cardinalidade e exploding join

O número de linhas pode crescer quando uma chave encontra múltiplas linhas do outro lado. Isso pode ser correto em uma relação 1:N ou indicar violação do grão esperado. Não deduplique automaticamente: primeiro confirme a regra de negócio e escolha uma ordenação determinística.

```sql
-- Diagnóstico do lado que deveria ter uma linha por loja
SELECT loja_id, count(*) AS quantidade
FROM dim_loja
GROUP BY loja_id
HAVING count(*) > 1;

-- Use somente quando a regra exigir a versão mais recente por loja
WITH dim_loja_atual AS (
  SELECT *
  FROM dim_loja
  QUALIFY row_number() OVER (
    PARTITION BY loja_id ORDER BY atualizado_em DESC, versao DESC
  ) = 1
)
SELECT f.id_venda, d.uf
FROM fato_vendas AS f
LEFT JOIN dim_loja_atual AS d ON f.loja_id = d.loja_id;
```

## Performance

O hint `BROADCAST` pode evitar shuffle da tabela grande quando o lado transmitido cabe com folga na memória dos executores. Confirme a estratégia no plano e não force broadcast apenas por contagem de linhas.

```sql
SELECT /*+ BROADCAST(d) */ f.id_venda, d.uf
FROM fato_vendas AS f
LEFT JOIN dim_loja AS d ON f.loja_id = d.loja_id;

EXPLAIN FORMATTED
SELECT f.id_venda, d.uf
FROM fato_vendas AS f
LEFT JOIN dim_loja AS d ON f.loja_id = d.loja_id;
```

Para skew, prefira primeiro AQE, filtragem antecipada e revisão das chaves. Salting é uma intervenção adicional e exige medir a distribuição e preservar a semântica.

## Cuidados

- Alinhe os tipos das chaves explicitamente; casts durante o join podem mascarar dados inválidos.
- `NULL = NULL` não é verdadeiro. Em Spark SQL, use `<=>` apenas quando nulos devam corresponder.
- Selecione apenas as colunas necessárias para reduzir leitura e transferência.
- Compare contagens e métricas antes e depois do join segundo o grão esperado.

## Checklist

- [ ] O grão de cada lado está declarado?
- [ ] A cardinalidade esperada é 1:1, 1:N ou N:N?
- [ ] Chaves têm tipos compatíveis e qualidade conhecida?
- [ ] O plano e as métricas confirmam a estratégia escolhida?

