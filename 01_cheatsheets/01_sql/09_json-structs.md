# JSON, Arrays e Structs (SQL)

## O que é

APIs e eventos costumam chegar como JSON: objetos aninhados e listas dentro de um único campo de texto. Em SQL você pode extrair campos do texto, convertê-lo em tipos nativos (`STRUCT`, `ARRAY`, `MAP`) ou armazená-lo como `VARIANT`.

## Extração direta de texto JSON

Para poucos campos de uma coluna `STRING` com JSON:

```sql
SELECT
    id,
    get_json_object(payload, '$.enderecos[0].geografia.codigo') AS cod_ibge,  -- JSONPath
    payload:cliente.nome::STRING                                AS nome_cliente, -- operador ':' do Databricks
    element_at(split(tags_texto, ','), 1)                       AS tag_principal -- índice começa em 1
FROM bronze.dados_api;
```

- `get_json_object` e o operador `:` devolvem `NULL` quando o caminho não existe — meça os nulos.
- Extrair muitos campos repetidamente reprocessa o texto a cada chamada; nesses casos converta uma vez com `from_json`.

## from_json: texto para tipos nativos

```sql
SELECT
    id,
    from_json(payload, 'STRUCT<cliente: STRUCT<id: INT, nome: STRING>, itens: ARRAY<STRUCT<cod: INT, valor: DECIMAL(10,2)>>>') AS dados
FROM bronze.dados_api;

-- Acesso por ponto depois de tipado
SELECT dados.cliente.nome, size(dados.itens) AS qtd_itens FROM silver.pedidos_json;
```

- `schema_of_json('<exemplo>')` sugere um schema a partir de uma amostra; revise antes de fixar.
- Registros que não seguem o schema geram campos `NULL`; valide-os.

## Explode: uma linha por elemento

`explode` muda o grão (de pedido para item). Faça isso só quando o grão desejado for o elemento, e leve junto a chave da origem.

```sql
-- Pedido 10 com itens [{cod:1, valor:20}, {cod:2, valor:30}] vira duas linhas
SELECT
    p.id_pedido,
    item.cod   AS cod_item,
    item.valor AS valor_item
FROM silver.pedidos AS p
LATERAL VIEW explode(p.itens) t AS item;

-- Sintaxe equivalente como função de tabela; posexplode traz a posição
SELECT p.id_pedido, e.pos, e.item.cod
FROM silver.pedidos AS p,
     LATERAL posexplode(p.itens) AS e(pos, item);
```

- `explode` descarta linhas com array vazio ou nulo; `explode_outer` as mantém com `NULL`.
- Para transformar arrays sem explodir, use funções de ordem superior: `transform`, `filter`, `aggregate`, `exists`.

```sql
SELECT id_pedido,
       aggregate(itens, CAST(0 AS DECIMAL(12,2)),
                 (acc, x) -> CAST(acc + x.valor AS DECIMAL(12,2)))           AS total_itens,  -- o acumulador mantém o tipo inicial
       filter(itens, x -> x.valor > 25)                                     AS itens_caros
FROM silver.pedidos;
```

## VARIANT para JSON semiestruturado

O tipo `VARIANT` (Databricks Runtime 15.3+) armazena JSON de forma binária e eficiente, sem schema fixo. É a opção recomendada para dados com estrutura instável que hoje ficam como `STRING`.

```sql
SELECT parse_json(payload) AS v FROM bronze.dados_api;          -- STRING → VARIANT
SELECT v:cliente.nome::STRING, try_variant_get(v, '$.itens[0].valor', 'DECIMAL(10,2)')
FROM bronze.eventos_variant;
```

- Referência: [VARIANT (Databricks)](https://docs.databricks.com/aws/en/semi-structured/variant).

## Checklist

- [ ] A extração preserva a chave do registro de origem?
- [ ] O novo grão após `explode` está documentado?
- [ ] Campos ausentes/incompatíveis são medidos?
- [ ] Para estruturas instáveis, `VARIANT` foi considerado?
