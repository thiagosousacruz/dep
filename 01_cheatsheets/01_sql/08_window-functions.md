# Window Functions em Spark SQL

> **Aprenda o conceito:** trilha [Window functions](../../03_trilhas/04_window-functions.md) — modelo mental, exemplo para prever e erros comuns.

## O que são

Funções de janela calculam valores relacionados sem reduzir o número de linhas como um `GROUP BY`. A especificação combina particionamento lógico, ordenação e, quando necessário, um frame.

## Exemplos

```sql
-- Versão mais recente por cliente; inclua desempate determinístico
SELECT *
FROM eventos
QUALIFY row_number() OVER (
  PARTITION BY cliente_id
  ORDER BY evento_em DESC, evento_id DESC
) = 1;

-- Comparação com a linha anterior
SELECT
  cliente_id,
  evento_em,
  valor,
  lag(valor) OVER (
    PARTITION BY cliente_id ORDER BY evento_em, evento_id
  ) AS valor_anterior
FROM eventos;

-- Acumulado desde o início da partição
SELECT
  conta_id,
  data_movimento,
  sum(valor) OVER (
    PARTITION BY conta_id
    ORDER BY data_movimento
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) AS saldo_acumulado
FROM movimentos;
```

## Rows versus range

`ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` cobre sete linhas, não sete dias. Para uma janela temporal, use uma expressão de ordenação e um `RANGE` compatíveis com a versão e o tipo de dado, ou agregue por data antes de usar `ROWS`.

## Cuidados de escala

Uma janela ordenada sem `PARTITION BY` forma uma única partição lógica e pode concentrar ordenação e estado em um executor. Ela ainda pode ser necessária para ranking global, mas deve ser usada conscientemente e medida na Spark UI. Não invente uma chave de partição apenas para acelerar: isso altera o resultado.

- Use colunas de desempate para resultados determinísticos.
- Evite partições extremamente grandes ou muito desbalanceadas.
- Projete apenas as colunas necessárias antes da janela.
- Verifique sort, shuffle, spill e duração das tarefas no plano e na UI.

## Checklist

- [ ] A partição representa o grupo lógico correto?
- [ ] A ordenação é determinística?
- [ ] O frame expressa linhas ou intervalo de valores como pretendido?
- [ ] O volume por partição foi medido?

