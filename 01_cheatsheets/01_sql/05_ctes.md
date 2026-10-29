# CTEs e Views Temporárias (Databricks / Spark SQL)

## O que é

Uma Common Table Expression (`WITH nome AS (...)`) nomeia um passo intermediário da consulta. Substitui subconsultas aninhadas por blocos sequenciais e legíveis. É uma construção **lógica**: não grava dados.

## CTEs para organizar a lógica

```sql
WITH clientes_ativos AS (
    SELECT id_cliente, nome, estado
    FROM silver.clientes
    WHERE status = 'ATIVO'
),
faturamento AS (
    SELECT id_cliente, SUM(receita) AS valor_comprado
    FROM silver.vendas
    WHERE ano = 2025
    GROUP BY id_cliente
)
SELECT c.nome, c.estado, f.valor_comprado
FROM clientes_ativos AS c
JOIN faturamento AS f USING (id_cliente);
```

- Um bloco por responsabilidade (filtrar, agregar, juntar) facilita testar cada passo isoladamente.
- Nomeie CTEs pelo conteúdo (`clientes_ativos`), não pela técnica (`cte1`).

## Views temporárias

`TEMP VIEW` guarda a definição de uma consulta durante a **sessão** (notebook ou conexão). Útil para inspecionar passos em células diferentes.

```sql
CREATE OR REPLACE TEMP VIEW v_qualidade_usuarios AS
SELECT *,
       CASE WHEN email IS NULL THEN 1 ELSE 0 END AS flag_erro_email
FROM bronze.usuarios;

SELECT * FROM v_qualidade_usuarios WHERE flag_erro_email = 1;
```

- A view some quando a sessão termina e não é visível para outras sessões.
- Global temp views (`global_temp`) não são suportadas em computação serverless; para compartilhar um resultado entre sessões, grave uma tabela.

## Reaproveitamento e materialização

Uma CTE referenciada várias vezes **pode** ser recalculada a cada referência ou ter a leitura reaproveitada — depende do plano (procure `ReusedExchange` ou `ReusedSubquery` no `EXPLAIN`). Não presuma nenhum dos dois: observe o plano (ver [Performance tuning](12_performance-tuning.md)).

```sql
EXPLAIN FORMATTED
WITH vendas_recentes AS (
    SELECT * FROM silver.vendas WHERE dt_venda >= DATE '2025-01-01'
)
SELECT 'norte' AS regiao, COUNT(*) FROM vendas_recentes WHERE regiao = 'N'
UNION ALL
SELECT 'sul', COUNT(*) FROM vendas_recentes WHERE regiao = 'S';
```

Quando o plano mostra recomputação cara de um passo usado várias vezes:

```sql
-- Clusters clássicos: cache em memória durante a sessão
CACHE TABLE vendas_recentes AS
SELECT * FROM silver.vendas WHERE dt_venda >= DATE '2025-01-01';
UNCACHE TABLE vendas_recentes;

-- Serverless (onde CACHE TABLE gera erro) ou resultado reutilizado por vários jobs:
CREATE OR REPLACE TABLE tmp.vendas_recentes AS
SELECT * FROM silver.vendas WHERE dt_venda >= DATE '2025-01-01';
```

- `CACHE TABLE` e as APIs de cache não são suportados em computação serverless: [limitações do serverless](https://docs.databricks.com/aws/en/compute/serverless/limitations).
- Tabela intermediária tem custo de escrita e de limpeza; meça antes e depois.

## CTE recursiva

`WITH RECURSIVE` percorre hierarquias (organogramas, árvores de categorias). Disponível a partir do Databricks Runtime 17.0 / DBSQL 2025.20 (Preview).

```sql
WITH RECURSIVE hierarquia (id, id_gestor, nivel) AS (
    SELECT id, id_gestor, 0 FROM rh.colaboradores WHERE id_gestor IS NULL
    UNION ALL
    SELECT c.id, c.id_gestor, h.nivel + 1
    FROM rh.colaboradores AS c
    JOIN hierarquia AS h ON c.id_gestor = h.id
)
SELECT * FROM hierarquia;
```

- O limite padrão é de 100 níveis de recursão (`RECURSION_LEVEL_LIMIT_EXCEEDED`); ciclos nos dados precisam ser tratados.
- Referência: [CTE (Databricks)](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-qry-select-cte).

## Checklist

- [ ] Cada CTE tem uma responsabilidade e um nome descritivo?
- [ ] O plano foi verificado antes de assumir recomputação ou reaproveitamento?
- [ ] O recurso de cache/materialização escolhido existe no tipo de computação usado?
