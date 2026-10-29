# Parsing de JSON, Arrays e Structs (SQL)

## O que é
APIs RESTFUL não retornam tabelas no modelo linhas e colunas (Tabular), elas enviam JSONs contendo Arrays de múltiplos objetos numa raiz só. E o Parquet em Datalakes armazena a string exata no grid de uma única linha/linha bruta.

## Nível Pleno/Sênior: Desempacotamento Escalar Direto
A técnica pra puxar 1 key simples de dentro da coluna gigantesca lotada de json formatando dinamicamente.

```sql
SELECT 
    id,
    
    -- Busca Segura com Extrator Indexado Nivel C (Spark Extrai):
    -- Extrai o parametro "codigo" dentro do bloco "geografia" na key_master json "enderecos" !
    get_json_object(coluna_json_pesada, '$.enderecos[0].geografia.codigo') AS cod_ibge,

    -- CASTANDO STRINGS GIGANTES EM ARRAYS REAIS E RECUPERANDO POSIÇÕES (Splittings)!
    element_at(split(tags_sujas_texto, ','), 1) as tag_principal_isolada
FROM dados_apis;
```

## Especialista (Sênior): Exploding The Array
Quando um pedido contém um array de itens, `explode` produz uma linha por item. Faça isso somente quando o grão desejado for item; a operação altera a cardinalidade e exige preservar a chave do registro de origem.

```sql
-- TABELA (Pedido 10, VlrTot: 50 | Array Itens: [{'cod':1, 'nf': 20}, {'cod':2, 'nf': 30}])

SELECT 
    db.pedido as PedidoFinal_Raiz,
    
    -- LÊ DINAMICAMENTE A TABELINHA INLINE QUE GERAMOS!
    item_aberto.cod AS CodigoIndividual_Fisico,
    item_aberto.nf AS NotaIndividual_Fisico
FROM db_restaurantes db
-- Produz uma linha por elemento do array e nomeia o elemento como item_aberto.
LATERAL VIEW EXPLODE(from_json(Array_itens, 'array<struct<cod:int,nf:int>>')) explode_tabela AS item_aberto;
```
