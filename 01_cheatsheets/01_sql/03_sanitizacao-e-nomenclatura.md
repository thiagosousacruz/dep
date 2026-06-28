# Sanitização Strings e Nomenclaturas (SQL/Silver Lyr)

## O que é
Rotinas cosméticas vitais pra garantir a confiabilidade estrutural. Textos digitados à mão via CRM quase nunca vem limpos na zona Bronze do Lake. Na passagem para Silver devemos higienizá-los e rebatizar as colunas exóticas pra padrões universais da CIA (`Snake_Case`), garantindo os cruzamentos futuros sem bugs.

## Nível Júnior/Pleno: Limpezas Primárias e AS (Alias)
Seu arsenal anti "*Espaços Fantasmas*". E a principal regra de ouro DE: Não confie no `SELECT *` de origens! Batize manualmente para travar o contrato de schemas.

```sql
-- Diga adeus aos nomes bizarros nativos como `VLR_FINAN_01` através do Alias explicito!
SELECT
    -- Higienização Básica de chaves texteis pre-joins ('   SAO pAULO ' -> 'SAO PAULO')
    UPPER(TRIM(cidade)) AS nm_cidade_padrao,
    LOWER(TRIM(email)) AS id_email_cadastro,
    
    -- Em caso de origens via legados DB em Windows ou Arquivos que chegaram quebrando e contendo espaços, isole-os em Crases Invertitadas (Backticks):
    `Data Venda Física` AS dt_venda,
    
    -- Dica: Booleanos sempre levam 'is_' ou 'has_'
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
