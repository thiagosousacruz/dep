# Sanitização de Strings e Nomenclatura em SQL

## O que é
Sanitização reduz variações de texto e nomes que dificultam joins, validações e consumo. Na passagem para Silver, aplique regras explícitas e rastreáveis; não altere valores apenas por estética e preserve o dado bruto na Bronze.

## Nível Júnior/Pleno: Limpezas Primárias e AS (Alias)
Projete e nomeie explicitamente as colunas publicadas. Isso torna alterações de schema visíveis e evita transportar campos desnecessários.

```sql
-- Converta nomes de origem para o padrão acordado no contrato de saída.
SELECT
    -- Higienização Básica de chaves texteis pre-joins ('   SAO pAULO ' -> 'SAO PAULO')
    UPPER(TRIM(cidade)) AS nm_cidade_padrao,
    LOWER(TRIM(email)) AS id_email_cadastro,
    
    -- Em caso de origens via legados DB em Windows ou Arquivos que chegaram quebrando e contendo espaços, isole-os em Crases Invertitadas (Backticks):
    `Data Venda Física` AS dt_venda,
    
    -- Convenção possível: prefixos is_ ou has_ para booleanos.
    FlgAtv AS is_ativo 
FROM lojas_filial;
```

## O Combate via REGEX (Expressão Regular)
Para sugeiras mais obscuras e pesadas do que apenas Trim simples conseguiria tratar, a Regex aplica substituições ou extrações padronizadas pelo core do Spark C++.

```sql
SELECT
    -- Removendo "Duplo Espaçamentos Internos Acidentais" por apenas "1 espaco simples".
    REGEXP_REPLACE(descricao_suja, ' +', ' ') AS desc_sem_espacamentos,
    
    -- Força Remoção do formato Máscara (Trazer APENAS ALFANUMERICOS num CPF). '[^N]' representa NEGAÇAO (Remova Tudo exceto o que ta aqui)
    REGEXP_REPLACE(cpf_com_mascara, '[^0-9]', '') AS cpf_intcto_hash
FROM user_logs;
```

## Nível Sênior: Match Fuzzy via Translate e Renomeações Físicas DDL
Se nome = `"Joao do Caminhao"` na origin do CRM 1 e Nome = `"João do Caminhão"` na origin 2, Inner Joins farão linhas vazarem! Remova na tora os acentos pra gerar bases neutras sem regex.

```sql
-- Translate é Matador. Ele troca todo caracter posicional pertencente ao bloco X pela sua versão limpa referenciada no bloco Y! E é super rápido.
SELECT 
    TRANSLATE(LOWER(nome_cadastrado), 'áàâãäéèêëíìîïóòôõöúùûüç', 'aaaaaeeeeiiiiooooouuuuc') AS nome_para_match_de_join
FROM pdvs;

-- DDL EM TABELAS PARA A ALTA CÚPULA ENGENHARIA 
-- Você enviou pra produção uma tabela inteira errada chamada 'id_prod' ao invez do convecional 'id_produto'. Ao invez de causar OVERWRITE de 3 horas em S3 refazendo a consulta, troques o log de catalog do schema nativamente:
ALTER TABLE db_silver.vendas RENAME COLUMN id_prod TO id_produto;
```
