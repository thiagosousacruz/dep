# Agrupamentos Relacionais e PIVOTS (Databricks)

## O que é
É o motor analítico primitivo utilizado para sumarização massiva de métricas nas tabelas e distorções da matriz (transformar linhas em colunas para os painéis de PowerBI).

## Nível Júnior/Pleno: Aglutinação Clássica e Atalhos Spark
Todo o atributo que não entrar nas funções matemáticas de empacotamento (`SUM()`, `MIN()`) deve ir obrigatoriamente para a linha delimitadora do `GROUP BY`. Em Databricks existem agregadores lógicos maravilhosos pra cortar CTEs.

```sql
SELECT 
    regiao_estoque, 
    -- 1. Agregacoes Convencionais
    COUNT(1) as qtd_encomendas,                 
    SUM(vlr_frete) as receita,
    
    -- 2. Agregações com Filter Incorporado (Evita case and when longos!)
    count_if(status = 'FALHA') AS compras_recusadas,             
    sum(vlr_frete) FILTER (WHERE canal = 'FISICA') AS receita_fim_fisica,
    
    -- 3. APPROX: O Segredo de Bilhões. 'COUNT(DISTINCT)' quebra clusters dando sorts inter-node. 
    -- approx_processa na hora c/ hyperLogLog (2% taxa de erro, ideal pra dashs!).
    approx_count_distinct(comprador_id) as clientes_aprox_ativos
    
FROM despachos_app
GROUP BY regiao_estoque             
HAVING sum(vlr_frete) > 100000;  -- FILTRA PÓS SOMA NO PACOTE!!!
```

## A Matriz Cruzada (PIVOT e UNPIVOT)
Uma das regras pesadas pra analistas que usam SQL. Converter linhas em metadados horizontais e vis-versa.

```sql
-- PIVOTAR: Quero que os "Anos" que chegam de pe na coluna ano_fiscal virem COLUNAS fixas na horizontal pros contadores verem na aba excel!
SELECT * FROM (
    SELECT regiao, ano_fiscal, SUM(vendas) as gmv FROM base_t GROUP BY regiao, ano_fiscal
)
PIVOT (
    SUM(gmv) 
    FOR ano_fiscal IN (2022, 2023, 2024) -- Pinos chaves do pivoteamento em hardcode
);

-- UNPIVOTAR (Spark 3.4+): Desfazer as abas esquisitas do excel (Coluna Janeiro, Coluna Fevereiro) em uma arvore vertical limpa (Coluna Mes, Coluna Valor).
SELECT * FROM planilhona_feia
UNPIVOT(
    receita_limpa FOR meses_desmontados IN (receita_jan, receita_fev, receita_mar)
);
```

## Nível Sênior: Totais e Sub-Totais (CUBE e ROLLUP)
Dispensa O `UNION ALL` recursivo gigante nos Dataframes para painéis burros que precisam consumir subtotais no backend. Multiplica os agrupadores internamente de 1x.

```sql
-- ROLLUP: Executa subtotais de forma hierárquica e decrescente (esquerda p dir.)
-- Retorna agrupamentos de: (Pais, Região, Estado), Depois solta linha de (Pais, Região), Depois so de (Pais) e No Fim uma Master Line de GRAND TOTAL (Tudo).
SELECT pais, regiao, estado, SUM(volume_caixas) FROM transporte_t
GROUP BY pais, regiao, estado WITH ROLLUP;

-- CUBE: Retorna TODAS as mutações e cruzas dimensionais (Ano sozinho com Regiao, Ano Com subproduto etc).
SELECT ano, tipo_produto, SUM(vendas) FROM faturamento 
GROUP BY ano, tipo_produto WITH CUBE;
```
