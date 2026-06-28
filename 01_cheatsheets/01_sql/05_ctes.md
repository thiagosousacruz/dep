# CTEs e Views Temporárias (Databricks / Spark SQL)

## O que é
As Common Table Expressions (CTEs), invocadas via cláusula `WITH`, permitem dividir complexidade brutal de Data Quality em pequenos blocos sequenciais e lógicos. Eliminam completamente as famosas e ilegíveis *Sub-queries aninhadas* em cascata, transformando consultas monolíticas em verdadeiros "Pipelines de Leitura".

## Nível Júnior: Organização Modular e Limpeza
O fim supremo de consultas no formato: `SELECT x FROM (SELECT y FROM (SELECT z FROM ...))`

```sql
-- 1. Desenvolvemos os blocos lógicos sequencialmente lendo arquivos originais apenas quando for vital
WITH ClientesAtivos AS (
    SELECT id, nome, estado
    FROM dim_clientes
    WHERE status = 'ATIVO'
),
FaturamentoTotal AS (
    SELECT cliente_id, SUM(receita) as valor_comprado
    FROM fatos_venda_2023
    GROUP BY cliente_id
)
-- 2. No bloco final, você cruza e orquestra apenas resultados lapidados com os filtros já impostos pelas CTEs
SELECT c.nome, c.estado, f.valor_comprado
FROM ClientesAtivos c
JOIN FaturamentoTotal f ON c.id = f.cliente_id;
```

## Nível Pleno: Quality Gates In-Memory (Via Sessão) e Views
No Databricks, quando CTEs tornam-se monstruosas de grandes por dezenas de `WITH`s e cruzamentos lógicos, testá-las em tela para debugar lógicas de ETL pode gerar um transtorno de blocos. A engenharia moderna utiliza Views Temporárias que persistem lógicas em tempo de runtime para você brincar em células posteriores.

```sql
-- Isole passos massivos gerando views virtuais. Ao fim do script ou ao término do Cluster, ela se dissolve inteiramente sem sujar o DB Silver.
CREATE OR REPLACE TEMP VIEW v_qualidade_dados AS
SELECT *, 
       IFF(email IS NULL, 1, 0) as flag_erro_email
FROM db_origem.bronze_usuarios;

-- A Partir daqui a tabeça virtual global está pronta! O motor passará pelo filtro em caso de chamada
SELECT * FROM v_qualidade_dados WHERE flag_erro_email = 1;
```

## Nível Sênior: O Perigo Absoluto da Reavaliação no Spark (Catalyst)
Arquitetos entendem um fator essencial do SQL: Modulos CTE e Views Temporárias **NÃO MATERIALIZAM dados no mundo físico**! Elas são equações lógicas. No ambiente Big Data do Spark, se você referenciar o nome da mesma CTE `A_Muito_Pesada` 3 vezes no escopo master, **O Spark vai ler o parquet inicial no Disco Rígido três vezes de forma idêntica!**

```sql
-- O ERRO GRAVE (Executará a origem gigante as requisições multiplicadas na árvore)
WITH CTE_Pesada AS (SELECT * FROM fatos_trilionaria WHERE dia > x)
SELECT * FROM a JOIN CTE_Pesada ON a.id = b.id -- Executa Disk Scan!
UNION ALL
SELECT * FROM b JOIN CTE_Pesada ON a.id = c.id -- Executa Disk Scan dnv!

-- A SOLUÇÃO: Quando precisar forçar os braços do cluster (Workers) a segurar o frame em RAM na execução de uma mesma lógica, exija o table cache na engine de plano virtual antes com views na execução em blocos.
CACHE VIEW cte_cacheada AS SELECT * FROM fatos_trilionaria;

SELECT * FROM a JOIN cte_cacheada...
UNION ALL
SELECT * FROM b JOIN cte_cacheada...
```
