# Tipos, Conversões e Timezones (SQL / Databricks)

## O que é

Comparar `100` (`INT`) com `'100'` (`STRING`) força conversões implícitas que podem quebrar joins, filtros e métricas sem erro aparente. Tipos explícitos estabilizam pipelines, principalmente em chaves, `MERGE`, datas e valores financeiros.

## CAST, TRY_CAST e modo ANSI

O Databricks SQL e o Spark 4.x usam modo ANSI por padrão: `CAST` de um valor inválido gera erro em vez de devolver `NULL`. Em origens instáveis, `TRY_CAST` converte valores inválidos em `NULL` para que sejam tratados explicitamente.

```sql
SELECT
    TRY_CAST(idade_txt AS INT)         AS idade,
    TRY_CAST(flag_ativo_txt AS BOOLEAN) AS is_ativo,
    idade_txt                           AS idade_original   -- preserve para auditoria
FROM bronze.cadastro;

-- Quantos valores foram perdidos na conversão?
SELECT count_if(idade_txt IS NOT NULL AND TRY_CAST(idade_txt AS INT) IS NULL) AS invalidos
FROM bronze.cadastro;
```

- Use `CAST` quando um valor inválido deve parar o pipeline; `TRY_CAST` quando ele deve ser medido e tratado.
- Confira o modo da sessão com `SET ansi_mode;` (Databricks SQL) ou `spark.sql.ansi.enabled` (clusters).

## DECIMAL para valores financeiros

`FLOAT` e `DOUBLE` são binários e aproximados: somas e arredondamentos podem divergir de uma conciliação. Use `DECIMAL(p, s)`.

```sql
SELECT
    CAST(vlr_saldo AS DECIMAL(18, 2))   AS saldo,
    TRY_CAST(aliquota AS DECIMAL(6, 4)) AS aliquota
FROM extrato_banco;
```

- `p` é o total de dígitos e `s` as casas decimais; dimensione `p` para o maior valor esperado mais a margem de somas.
- Operações entre decimais podem ampliar precisão e escala; faça o `CAST` final na publicação.

## Datas, formatos e timezone

`current_date()` e `current_timestamp()` seguem o timezone da sessão. O erro comum é misturar timestamps armazenados em UTC com sessões em outro fuso sem conversão explícita.

```sql
SET TIME ZONE 'America/Sao_Paulo';   -- fixa o fuso da sessão/job quando a regra exige

SELECT
    from_utc_timestamp(ts_evento_utc, 'America/Sao_Paulo')     AS ts_evento_br,  -- só se a origem estiver em UTC
    to_date(data_txt, 'dd-MM-yyyy')                            AS data_ref,
    to_timestamp(data_hora_txt, 'dd-MM-yyyy HH:mm:ss')         AS ts_ref,
    try_to_timestamp(data_hora_txt, 'dd-MM-yyyy HH:mm:ss')     AS ts_ref_seguro,
    date_add(DATE '2024-01-01', 30)                            AS trinta_dias_depois,
    datediff(DATE '2024-12-31', DATE '2024-01-01')             AS dias_corridos,
    date_trunc('MONTH', ts_evento_utc)                         AS inicio_do_mes
FROM logs;
```

- Padrões de formato: `MM` é mês e `mm` é minuto; `HH` é 0–23 e `hh` é 1–12.
- Com ANSI ligado, `to_timestamp` falha em texto inválido; `try_to_timestamp` devolve `NULL`.
- Use literais tipados (`DATE '2024-01-01'`, `TIMESTAMP '...'`) para não depender de conversão implícita.

## Cuidados

- Padronize tipos antes de joins e `MERGE INTO`; casts dentro da condição de join escondem dados inválidos.
- Documente a regra de timezone da pipeline: armazenamento (geralmente UTC), sessão e exibição.
- Meça os `NULL` gerados por `TRY_CAST` em vez de descartá-los silenciosamente.

## Checklist

- [ ] O modo ANSI do ambiente é conhecido?
- [ ] Valores monetários usam `DECIMAL`?
- [ ] O fuso de origem de cada timestamp está documentado?
- [ ] Conversões inválidas são contadas e monitoradas?
