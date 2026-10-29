# Sanitização de Strings e Nomenclatura (SQL)

## O que é

Sanitização reduz variações de texto que dificultam joins, validações e consumo. Na passagem para Silver, aplique regras explícitas e rastreáveis; não altere valores só por estética e preserve o dado bruto na Bronze.

## Limpeza básica e aliases

Projete e nomeie explicitamente as colunas publicadas. Isso torna mudanças de schema visíveis e evita transportar campos desnecessários.

```sql
SELECT
    UPPER(TRIM(cidade))    AS nm_cidade,         -- '  sao pAULO ' -> 'SAO PAULO'
    LOWER(TRIM(email))     AS ds_email,
    `Data Venda Física`    AS dt_venda,          -- nomes com espaço/acento exigem crases
    FlgAtv                 AS is_ativo           -- convenção: is_/has_ para booleanos
FROM bronze.lojas_filial;
```

- Defina uma convenção (prefixos `id_`, `dt_`, `vl_`, `is_`; `snake_case`) e documente-a no contrato da tabela.
- `TRIM` remove apenas espaços; para tabulações e quebras de linha use expressão regular.

## Expressões regulares

```sql
SELECT
    REGEXP_REPLACE(descricao, '\\s+', ' ')             AS descricao_normalizada, -- colapsa espaços, tabs, quebras
    REGEXP_REPLACE(cpf_com_mascara, '[^0-9]', '')      AS cpf_digitos,          -- mantém só dígitos
    REGEXP_EXTRACT(email, '@(.+)$', 1)                 AS dominio_email,
    email RLIKE '^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$'        AS email_formato_valido
FROM bronze.usuarios;
```

- Em literais SQL do Spark, a barra invertida é escapada: `'\\s'` vira o regex `\s`.
- Regex é mais cara que funções simples (`TRIM`, `REPLACE`, `TRANSLATE`); use quando o padrão realmente exigir.

## Remoção de acentos com TRANSLATE

`TRANSLATE` substitui cada caractere do segundo argumento pelo da mesma posição no terceiro. É útil para gerar chaves de comparação sem acentos (`'João do Caminhão'` vs `'Joao do Caminhao'`).

```sql
SELECT
    TRANSLATE(LOWER(nome),
              'áàâãäéèêëíìîïóòôõöúùûüç',
              'aaaaaeeeeiiiiooooouuuuc') AS nome_chave_match
FROM pdvs;
```

- Use o resultado como **chave de comparação**, não como valor publicado.
- A lista cobre o português comum; outros caracteres (ex.: `ñ`) precisam ser acrescentados. Para matching aproximado de verdade (erros de digitação), avalie funções como `levenshtein` e regras de negócio específicas.

## Renomear colunas em tabelas Delta

Em Delta, `RENAME COLUMN` e `DROP COLUMN` exigem **column mapping** habilitado na tabela. Com ele, a operação altera só metadados, sem reescrever os dados.

```sql
ALTER TABLE silver.vendas SET TBLPROPERTIES ('delta.columnMapping.mode' = 'name');
ALTER TABLE silver.vendas RENAME COLUMN id_prod TO id_produto;
```

- Habilitar column mapping atualiza o protocolo da tabela (leitores antigos podem deixar de ler) e pode afetar Change Data Feed e leituras em streaming dessa tabela.
- Consumidores que referenciam o nome antigo quebram: trate como mudança de contrato.
- Referência: [Delta column mapping (Databricks)](https://docs.databricks.com/aws/en/delta/column-mapping).

## Checklist

- [ ] A regra de limpeza está documentada e é reversível a partir da Bronze?
- [ ] Chaves de match sem acento são usadas só para comparação?
- [ ] Renomeações em tabelas publicadas foram comunicadas aos consumidores?
