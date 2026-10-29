# Profiling e Checagens de Data Quality (SQL)

## O que é

Muitos problemas de dados não geram erro: a consulta roda e o defeito só aparece no KPI. Checagens curtas e frequentes validam grão, unicidade, nulos, faixas e distribuição antes de publicar.

## Grão e unicidade

Compare o número de linhas com o número de chaves distintas **do grão esperado**.

```sql
-- Saída deveria ter 1 linha por pedido
SELECT
    COUNT(*)                   AS linhas,
    COUNT(DISTINCT id_pedido)  AS pedidos_distintos,
    COUNT(*) - COUNT(DISTINCT id_pedido) AS excedente
FROM gold.fato_pedidos;

-- Quais chaves estão duplicadas?
SELECT id_pedido, COUNT(*) AS n
FROM gold.fato_pedidos
GROUP BY id_pedido
HAVING COUNT(*) > 1
ORDER BY n DESC
LIMIT 20;
```

## Nulos e faixas impossíveis

```sql
SELECT
    count_if(id_cliente IS NULL)             AS clientes_nulos,
    ROUND(100 * AVG(CASE WHEN email IS NULL THEN 1 ELSE 0 END), 2) AS pct_email_nulo,
    MIN(idade)                               AS idade_min,
    MAX(idade)                               AS idade_max,
    count_if(valor_bruto < 0)                AS valores_negativos,
    count_if(dt_evento > current_date())     AS datas_futuras
FROM silver.cadastro;
```

## Distribuição por categoria

```sql
SELECT
    tipo_assinatura,
    COUNT(*)                                             AS linhas,
    ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 2)     AS pct
FROM silver.contratos
GROUP BY tipo_assinatura
ORDER BY linhas DESC;
```

Compare com a execução anterior: uma categoria que some ou dobra costuma indicar problema na origem.

## Expectativas na própria tabela

Restrições `CHECK` em tabelas Delta impedem gravar linhas que violem a regra.

```sql
ALTER TABLE silver.cadastro ADD CONSTRAINT idade_valida CHECK (idade BETWEEN 0 AND 120);
ALTER TABLE silver.cadastro ALTER COLUMN id_cliente SET NOT NULL;
```

- A escrita inteira falha se uma linha violar a restrição; decida se isso é o comportamento desejado ou se prefere quarentena.
- Em pipelines declarativos (Lakeflow / DLT), `EXPECT ... ON VIOLATION DROP ROW | FAIL UPDATE` registra métricas por regra.

## Checklist

- [ ] O grão esperado está declarado e testado?
- [ ] Nulos em campos críticos têm limite aceitável definido?
- [ ] Existe comparação com a execução anterior (volume e distribuição)?
- [ ] Regras estáveis viraram restrições na tabela?
