# NULL e lógica de três valores

> **Objetivo:** prever o efeito de `NULL` em comparações, filtros, agregações, joins e `NOT IN`, e escolher explicitamente o tratamento certo. **Tempo:** 1 h. **Pré-requisitos:** [Ordem lógica do SQL](01_ordem-logica-do-sql.md).

## O problema

A lista de "clientes não bloqueados" volta vazia. O filtro "telefone diferente de 11" some com os clientes sem telefone. A média de nota sobe depois de uma carga com muitas notas faltando. Nenhuma dessas consultas dá erro. Em todas, alguém tratou `NULL` como se fosse um valor; na verdade ele significa **"desconhecido"**.

## Modelo mental

- **Comparar com desconhecido dá desconhecido.** `NULL = 1`, `NULL <> 1` e até `NULL = NULL` resultam em `NULL`, não em `false`.
- **Existem três valores lógicos: verdadeiro, falso e desconhecido.**

```text
AND      | true   false  NULL         OR       | true   false  NULL
true     | true   false  NULL         true     | true   true   true
false    | false  false  false        false    | true   false  NULL
NULL     | NULL   false  NULL         NULL     | true   NULL   NULL
                                       NOT NULL → NULL
```

- **`WHERE`, `HAVING`, `ON` e `CASE WHEN` só aceitam verdadeiro.** Desconhecido é tratado como "não passa", por isso a linha some em silêncio.
- **Agregações ignoram `NULL`** (exceto `COUNT(*)`). `AVG` tira o nulo do numerador *e* do denominador.
- **Para tratar `NULL` como valor comparável**, use `IS NULL`, `<=>` (ou `IS NOT DISTINCT FROM`) e `coalesce`, sempre de propósito.

## Exemplo para prever

```sql
CREATE OR REPLACE TEMP VIEW clientes AS
SELECT * FROM VALUES (1, 'Ana', '11'), (2, 'Bia', NULL), (3, 'Caio', '21'), (NULL, 'Sem id', '31')
AS t(id, nome, telefone);

CREATE OR REPLACE TEMP VIEW bloqueados AS
SELECT * FROM VALUES (2), (CAST(NULL AS INT)) AS t(id);

-- A
SELECT nome FROM clientes WHERE telefone <> '11';
-- B
SELECT COUNT(*), COUNT(telefone), COUNT(DISTINCT id) FROM clientes;
-- C
SELECT nome FROM clientes WHERE id NOT IN (SELECT id FROM bloqueados);
-- D
SELECT nome FROM clientes c
WHERE NOT EXISTS (SELECT 1 FROM bloqueados b WHERE b.id = c.id);
```

Resultado esperado:

- **A:** `Caio`, `Sem id`. Bia some: `NULL <> '11'` é desconhecido.
- **B:** `4, 3, 3`. `COUNT(coluna)` e `COUNT(DISTINCT)` ignoram nulos.
- **C:** **nenhuma linha.** `id NOT IN (2, NULL)` vira `id <> 2 AND id <> NULL`, e o segundo termo é sempre desconhecido.
- **D:** `Ana`, `Caio`, `Sem id`. `NOT EXISTS` só pergunta se existe um par igual; como `NULL` não é igual a nada, até o cliente sem id passa. Decida se isso é o que você quer.

Em PySpark a semântica é a mesma: `F.col("telefone") != "11"` descarta os nulos, e `eqNullSafe` corresponde a `<=>`.

```python
from pyspark.sql import functions as F

clientes.filter((F.col("telefone") != "11") | F.col("telefone").isNull())   # inclui quem não tem telefone
clientes.join(bloqueados, "id", "left_anti")                                 # equivalente seguro ao NOT IN
```

## Quebre de propósito

1. **Tabela verdade.** Rode `SELECT NULL = NULL, NULL <=> NULL, NULL AND false, NULL OR true, NOT NULL`. Confira: `NULL, true, false, true, NULL`.
2. **`CASE` com `= NULL`.** `CASE WHEN telefone = NULL THEN 'sem' ELSE 'com' END` classifica *todos* como `com`. Troque por `IS NULL`.
3. **Média enganosa.** `SELECT AVG(x), AVG(coalesce(x, 0)) FROM VALUES (10), (NULL), (20) AS t(x)` → `15` e `10`. Qual responde à pergunta de negócio: "nota média de quem respondeu" ou "nota média por envio"?
4. **Soma de nada.** `SUM` de uma coluna só com nulos devolve `NULL`, não `0`, enquanto `COUNT` devolve `0`. Veja como isso afeta um painel.
5. **Concatenação.** `concat('a', NULL)` é `NULL`; `concat_ws('-', 'a', NULL, 'b')` é `a-b`. `1 + NULL` é `NULL`.
6. **Agrupamento e ordenação.** No `GROUP BY`, os nulos formam **um grupo só**. Em `ORDER BY x` (crescente) eles vêm primeiro, e em `ORDER BY x DESC` vêm por último. Use `NULLS FIRST/LAST` para deixar explícito.

## Erros comuns e como diagnosticar

- **`NOT IN` com subconsulta voltando vazio** → algum valor nulo na subconsulta. Troque por `NOT EXISTS` ou `LEFT ANTI JOIN`.
- **Filtro `<>` "perdendo" linhas** → os nulos foram descartados. Decida e escreva: `OR col IS NULL`, ou `NOT (col <=> valor)`.
- **Join perdendo linhas** → chaves nulas não se casam com `=`. Conte as chaves nulas de cada lado antes de cruzar.
- **`fillna`/`coalesce` aplicado sem critério** → troca "desconhecido" por um valor falso (0, `'N/A'`) e distorce médias e contagens. Documente a regra.

## Cheque seu entendimento

1. Por que `NULL = NULL` não é verdadeiro?
2. O que o `WHERE` faz com uma condição desconhecida?
3. Por que um único nulo na subconsulta zera o `NOT IN`?
4. Qual a diferença entre `COUNT(*)` e `COUNT(coluna)`?
5. Quando `coalesce(nota, 0)` é correto e quando distorce o resultado?

<details markdown="1">
<summary>Respostas</summary>

1. NULL significa "desconhecido". Comparar dois desconhecidos dá desconhecido (UNKNOWN), não verdadeiro. Para comparar com segurança, use `<=>` ou `IS NULL`.
2. Descarta a linha. O `WHERE` só mantém o que é TRUE; FALSE e UNKNOWN saem.
3. `x NOT IN (a, NULL)` equivale a `x <> a AND x <> NULL`. A segunda parte é sempre UNKNOWN, então o resultado nunca é TRUE. Use `NOT EXISTS` ou `LEFT ANTI JOIN`.
4. `COUNT(*)` conta linhas; `COUNT(coluna)` conta só as linhas em que a coluna não é nula.
5. É correto quando ausente *significa* zero pela regra de negócio, como "sem desconto". Distorce quando significa "não informado": a média cai porque desconhecidos viram zeros.

</details>

## Próximos passos

- **Consulta:** [NULL em agregações e comparações](../01_cheatsheets/01_sql/04_nulos-e-condicionais.md#null-em-agregacoes-e-comparacoes) · [Filtros: IN, BETWEEN e LIKE](../01_cheatsheets/01_sql/01_sintaxe-basica.md#filtros-in-between-e-like) · [when / otherwise e coalesce no PySpark](../01_cheatsheets/02_pyspark/05_nulos-e-condicionais.md#when-otherwise-e-coalesce)
- **Prática:** [desafio de NULL em agregações](../desafio.html?id=sql-04-null-agregacoes) · [desafio de COALESCE e CASE](../desafio.html?id=sql-04-coalesce-case) · [desafio de percentual de nulos](../desafio.html?id=spk-12-nulos-coluna)
- **Aplicação real:** em uma tabela autorizada, meça o percentual de nulos das colunas usadas em filtros e chaves de join. Revise uma consulta que use `NOT IN` ou `<>` sobre essas colunas.
