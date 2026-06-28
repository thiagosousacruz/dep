# Condicionais e Preenchimento Nulos (SQL)

## O que é
O estado `NULL` assombra analíticas. Ele não significa *vazio string ('')* e não é *Zero*. É pura e simplesmente um vazio bytes `Ausência de Estado`. Deixá-los vazar sem regras quebra agrupadores e derruba pontes de Joinings de paineis PowerBI (Deixando linhas como chaves vazias desamarradas na Dimension table).

## Nível Júnior/Pleno: Condicionais e Controle Básico (`COALESCE`)
Abstraindo vácuos de dados para nomenclaturas seguras na tabela. O SQL `COALESCE(coluna, valor)` olha da esquerda pra direita a lista e para assim que não achar nulo. Muito melhor que codificar gigantes `CASE WHEN` para testes base.

```sql
SELECT 
    id_produto,
    -- Converte Nulos Textuais
    COALESCE(nome_produto, 'SEM NOME ORIGINAL') AS descricao_valida,
    
    -- ESTRATEGIA CHAVE ORFA: Crie um FK default! Um produto que venha sem a Categoria receberá '-1', la na Tabela De Categoria do BI, crie um campo default '-1 - Orfão'. O Link do Join baterá perfeitamente sem erros! 
    COALESCE(id_categoria, -1) AS id_categoria,
    
    -- O CASE WHEN classico para condicoes densas (Sempre defina o ELSE Final!)
    CASE 
        WHEN status_atual = 'A' THEN 'ALTO_RISCO'
        WHEN status_atual = 'M' AND is_ativo = True THEN 'MEDIO_RISCO'
        ELSE 'BAIXO_RISCO'
    END as flag_risco
FROM base_catalogo;
```

## O Impacto Oculto em Contagens
Todo agrupador matemático clássico varre e mata a existencia de nulos na hora de somar volumes. `COUNT(1)` conta FÍSICO a partição, `COUNT(coluna)` varre o NULO e queima a linha.

```sql
SELECT 
    COUNT(1) AS fisicas_totais_puras,             -- Conta até as linhas completamentes em branco = 10 
    COUNT(id_celular_reserva) AS qty_preenchidos  -- Retornará só 3 (Pq as outras 7 pessoas não mandaram dados!).

FROM envios;
-- ALERTA: Nunca realize INNER JOINS entre duas chaves caso ambas sejam NULAS! A = NULL e B = NULL não vão triggar ligações no SQL nativo pois ele recusa que nulo empate com nulo sem ser de forma explícita na semantica `IS NULL` !
```

## Nível Sênior: Manipulando Operadores Dinâmicos (Flags & Nullifs)
Engenheiros criam *Quality Flags*: Nós inserimos colunistas int ocultas atestando qualidade da origem.
E também temos de prevenir falhas matemáticas nas queries!

```sql
SELECT 
    b.valor_bruto,
    a.comissao_fixa,
    
    -- ERRO FATAL: "b.valor_bruto / a.comissao" !!!
    -- SE A COMISSAO VIER '0' DO BACKEND, ISSO É DIVISÃO POR ZERO! SEU JOB CRASH E TE ACORDA AS 3 DA MANHA.
    -- SALVACAO: O "NULLIF(coluna, valor)". Se B for 0, converta forçadamente para NULL. Dividir por Nulo não dá erro fatal, apenas volta NULO pra casinha no output final !
    b.valor_bruto / NULLIF(a.comissao_fixa, 0) as fator_multiplicador,
    
    -- Geracao de Flag p/ dashboarding de DQ
    IFF(a.comissao_fixa IS NULL, 1, 0) as is_linha_com_sintoma_furo
FROM fatos a;
```
