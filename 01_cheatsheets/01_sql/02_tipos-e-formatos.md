# Tipos, Conversoes e Timezones (SQL/Databricks)

## O que e
Em big data, cruzar `100` (`INT`) com `"100"` (`STRING`) e um caminho classico para erro silencioso, joins quebrados e metricas inconsistentes. A tipagem forte ajuda a estabilizar pipelines, especialmente em joins, merges, datas e campos financeiros.

## Nivel Junior/Pleno: Protegendo a Tipagem (`TRY_CAST`)
Quando a origem vem suja, `CAST(...)` pode abortar a execucao inteira. Em cargas operacionais, prefira `TRY_CAST(...)` para transformar valores invalidos em `NULL` e tratar isso explicitamente depois.

```sql
SELECT
    TRY_CAST(idade_txt AS INT) AS idade_segura,
    TRY_CAST(flag_ativo_txt AS BOOLEAN) AS is_ativo
FROM camada_bronze;
```

## Decimal para valores financeiros
Evite `FLOAT` e `DOUBLE` para dinheiro. Em somatorias, arredondamentos e conciliacoes, o comportamento de ponto flutuante pode gerar divergencias.

```sql
SELECT
    CAST(vlr_saldo AS DECIMAL(16,4)) AS saldo_financeiro_restrito,
    TRY_CAST(imposto AS DECIMAL(6,2)) AS aliquota
FROM extrato_banco;
```

## Nivel Senior: Parsing de datas e timezone com regra explicita
Em Databricks/Spark, `current_date()` e `current_timestamp()` seguem o timezone efetivo da sessao. O erro mais comum nao e a funcao em si, e sim misturar timestamps armazenados em UTC com sessoes configuradas em outro fuso sem conversao explicita.

```sql
-- 1. Quando a regra operacional exigir consistencia local, fixe o timezone da sessao/job
SET TIME ZONE 'America/Sao_Paulo';

SELECT current_timestamp() AS agora_sessao_br;

-- 2. Use from_utc_timestamp apenas quando a coluna de origem estiver efetivamente em UTC
SELECT
    from_utc_timestamp(ts_evento_utc, 'America/Sao_Paulo') AS ts_evento_br,

    -- 3. Parsing formatado para strings fora do padrao ANSI
    to_date(data_referencia_ext, 'dd-MM-yyyy') AS data_ajustada,
    to_timestamp(data_sistema_ext, 'dd-MM-yyyy HH:mm:ss') AS timestamp_ajustado,

    -- 4. Operadores analiticos de data
    date_add('2024-01-01', 30) AS trinta_dias_depois,
    datediff('2024-12-31', '2024-01-01') AS diff_dias_corrida
FROM logs;
```

## Erros comuns
- Usar `CAST` direto em origem instavel e derrubar o job por um unico valor invalido.
- Salvar valor financeiro em `FLOAT` ou `DOUBLE`.
- Fazer join entre colunas logicamente iguais, mas com tipos diferentes.
- Converter timezone sem saber se a coluna original esta em UTC, horario local ou timezone de sessao.

## Boas praticas
- Padronize tipos antes de joins e `MERGE INTO`.
- Prefira `TRY_CAST` em origem Bronze e trate os `NULLs` gerados de forma consciente.
- Declare `DECIMAL(p, s)` para valores monetarios.
- Documente a regra de timezone da pipeline: sessao local, UTC de armazenamento e conversao de exibicao.
