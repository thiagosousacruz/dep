# Sintaxe Básica Executiva (SQL / Databricks)

## O que é
A sintaxe ANSI fundamental. Para um engenheiro júnior recém-chegado, o SQL pode até ser intuitivo de ler, mas a **ordem de execução** nos bastidores obedece a regras muito rígidas. Se você tentar filtrar o resultado de uma equação na cláusula errada, o Spark devolverá erros ou lerá base à toa.

## Nível Júnior: Ordem de Execução e O Esqueleto Clássico
A forma como escrevemos é diferente da forma como o banco lê os dados!
**Ordem que Lemos:** `SELECT -> FROM -> WHERE -> GROUP BY -> HAVING -> ORDER BY`
**Ordem que o Engine Processa:** `FROM -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY`.

```sql
-- O Esqueleto Completo
SELECT 
    categoria_id,              -- 5º A ser processado (Escolhe os campos da output real)
    SUM(valor) AS receita
FROM tabela_master             -- 1º A Origem Principal dos dados
WHERE status_venda = 'FECHADA' -- 2º Corta os Lixos fora ANTES de qualquer Cáculo!
GROUP BY categoria_id          -- 3º Empacota as Linhas Restantes Filtradinhas 
HAVING SUM(valor) > 1000       -- 4º Filtra RESULTADOS das somas!! (Não use o WHERE pra isso!)
ORDER BY receita DESC          -- 6º Ordena Visualmente
LIMIT 10;                      -- 7º Corta pra tela apenas os top 10
```

## Operadores Lógicos Críticos e Subconjuntos
Como encontrar múltiplas informações sem enfileirar infinitos `OR`s.

```sql
SELECT *
FROM banco_central
WHERE
    -- Lista de Elementos Seguros (Nunca use a = 1 OR a = 2 OR a = 3)
    sigla_estado IN ('SP', 'RJ', 'MG') 
    
    -- Intervalos (BETWEEN). Inclui as bordas/Limites informados! (Entre o dia 01 e 05)
    AND data_nascimento BETWEEN '2000-01-01' AND '2000-01-05'
    
    -- Procura Parcial (LIKE). O '%' funciona como um "Coringa Absoluto"
    AND nome_cliente LIKE 'THIAGO%'   -- Tudo que COMEÇA por Thiago.
    AND nome_falso LIKE '%SILVA%'     -- Tem SILVA em qualquer lugar (Meio, Fim, Começo!)
    
    -- Exceções
    AND status_conta NOT IN ('CANCELADO', 'BLOQUEADO');
```

## Nível Pleno/Sênior: DISTINCT e Boas Práticas Operacionais
O Analista Júnior muitas vezes apela pro `SELECT DISTINCT *` para curar qualquer duplicação por medo. O Engenheiro sabe que um DISTINCT é uma das operações de Hash Shuffle mais pesadas possíveis numa nuvem de rede em banco massivo.

```sql
-- ❌ EVITE O DISTINTO GLOBAL DE MEDO
SELECT DISTINCT * FROM fato_gigantesca; -- Gastará horas para o cluster empacotar o mundo inteiro atoa.

-- ✅ BOAS PRÁTICAS: Dedique Unique Views pontuais!
SELECT DISTINCT id_cliente 
FROM clientes_ativos 
WHERE id_cliente IS NOT NULL; -- Use Distinct cirurgicamente pra extrair Chaves puras atômicas para futuros cruzamentos Ctes.
```

## Operadores de Conjunto (Set Operations)
Úteis para empilhar resultados ou comparar a diferença exata entre duas queries (muito usado em validações de qualidade e migrações).

```sql
-- UNION ALL: Empilha tudo rapidamente (mantém duplicatas). É muito mais rápido que UNION.
SELECT id_user FROM base_antiga
UNION ALL
SELECT id_user FROM base_nova;

-- UNION: Empilha e faz um DISTINCT implícito (mais pesado).
SELECT id_user FROM base_antiga
UNION
SELECT id_user FROM base_nova;

-- EXCEPT (ou MINUS): Retorna o que tem na consulta A e NÃO TEM na consulta B.
-- Excelente para encontrar registros perdidos em migrações ou cruzamentos.
SELECT id_transacao FROM extrato_banco
EXCEPT
SELECT id_transacao FROM base_conciliada;

-- INTERSECT: Retorna apenas o que existe em AMBAS as consultas.
SELECT id_produto FROM catalogo_site
INTERSECT
SELECT id_produto FROM estoque_fisico;
```
