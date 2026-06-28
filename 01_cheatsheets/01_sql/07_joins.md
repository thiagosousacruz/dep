# SQL Joins (Databricks / Spark SQL)

## O que e
Joins combinam linhas de duas ou mais tabelas a partir de uma chave em comum. Em Databricks/Spark, tambem sao uma das operacoes mais custosas, porque costumam mover dados entre particoes e nodes do cluster.

## Nivel Junior: Mapa minimo dos joins

```sql
-- INNER JOIN: mantem apenas o que existe nas duas tabelas
SELECT f.venda, dim.uf_estado
FROM Tb_Fatos f
INNER JOIN Dim_Geografia dim ON f.geografia_id = dim.id;

-- LEFT JOIN: mantem tudo da esquerda e busca complemento na direita
SELECT f.venda, dim.uf_estado
FROM Tb_Fatos f
LEFT JOIN Dim_Geografia dim ON f.geografia_id = dim.id;

-- FULL OUTER JOIN: bom para auditoria de divergencias
SELECT a.id, b.id
FROM tabela_a a
FULL OUTER JOIN tabela_b b ON a.id = b.id;

-- CROSS JOIN: produto cartesiano, use apenas de forma intencional
SELECT a.id, b.faixa
FROM tabela_a a
CROSS JOIN tabela_b b;
```

## O terror do Databricks: Exploding Joins
O erro classico e fazer join com uma dimensao/tabela da direita que possui mais de uma linha por chave. Quando isso acontece, a fato e multiplicada sem aviso e os numeros finais ficam incorretos.

```sql
WITH Dimensao_Sanitizada AS (
    SELECT *
    FROM Lixo_Dimensional_B
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY id
        ORDER BY updatetime DESC
    ) = 1
)
SELECT ...
FROM fato_a
LEFT JOIN Dimensao_Sanitizada b ON fato_a.id = b.id;
```

## Nivel Pleno: Semi e Anti Joins
Esses joins filtram sem trazer colunas extras, e sao muito uteis para existencia e ausencia.

```sql
-- LEFT SEMI JOIN: traz linhas da esquerda que existem na direita
SELECT a.id, a.nome
FROM clientes a
LEFT SEMI JOIN logs b ON a.id = b.id_comprador;

-- LEFT ANTI JOIN: traz linhas da esquerda que nao existem na direita
SELECT r.id, r.nome
FROM clientes_base r
LEFT ANTI JOIN acesso_apps x ON r.id = x.id_sessao;
```

## Nivel Senior: Hints e performance

```sql
-- BROADCAST JOIN: use quando a tabela da direita for pequena o suficiente
SELECT /*+ BROADCAST(dim) */ f.venda, dim.loja
FROM fato_gigantesca_de_vendas f
LEFT JOIN dimensao dim ON f.loja_id = dim.id;

-- SKEW JOIN: ajuda em cenarios de desbalanceamento forte de chaves
SELECT /*+ SKEW('tabela_desbalanceada_suja') */ a.id, b.valor
FROM tabela_desbalanceada_suja a
JOIN dim_valores b ON a.id = b.id;
```

## Boas práticas (Heurísticas do dia a dia)

- **Evite o Exploding Join por padrão:** Não assuma que a tabela da direita (dimensão) tem apenas uma linha por chave. Se a regra de negócio dita que a relação é 1:1, **sempre deduplique o lado direito com `QUALIFY ROW_NUMBER() = 1`** antes do join. Isso salva horas de *troubleshooting*.
- **Check de sanidade obrigatório:** Adquira o hábito de rodar a seguinte query mental (ou física) antes de aprovar um Pull Request: "A tabela A tem X linhas. Após o LEFT JOIN com a tabela B, a tabela final continua com X linhas?". Se o número aumentou, você gerou um produto cartesiano acidental.
- **Evite joins em colunas de tipos diferentes:** Um `JOIN` entre um `INT` e um `STRING` fará com que o Databricks faça um *implicit cast*, destruindo o uso de índices e particionamentos. Sempre alinhe os tipos com `CAST()` ou `TRY_CAST()`.
- **Cuidado com Nulos nas chaves:** Em um `INNER JOIN` normal, `NULL = NULL` retorna FALSO. Se precisar cruzar registros onde a chave pode ser nula dos dois lados, use a sintaxe `NULL-SAFE EQUAL` do Spark: `ON a.chave <=> b.chave`.
- **Não faça `SELECT a.*, b.*`:** Joins em larga escala com select asterisco arrastam gigabytes de colunas inúteis pela rede do cluster (*Network I/O*). Traga apenas o estritamente necessário.
