# Window Functions (Databricks / Spark SQL)

## O que é
Operadores especiais que resolvem as perguntas temporais sem amassar a matriz em group bys (`ORDER BY OVER()`). Eles realizam as equações consultando "vizinhos indexados sequenciais" pelas regras da aba `PARTITION BY`, e retêm formatações linha a linha originais!

## Nível Júnior: Rankings e Deduplicações Analíticas
Você já limpou nulos, limpou as crases e explodings, agora limpe as linhas velhas repetitivas preservando chaves atomicamente únicas na Silver!

```sql
-- Sintaxe Fixa Mestre:  OVER(PARTITION BY ... ORDER BY ...)
SELECT 
    id_maquina, data_status, log_critico,
    
    -- ROW_NUMBER: Absolutamente Inegociável para desempates estritos das pipelines Silver ! (Se empatou.. joga pro ladinho pulando num!). Pede as 1 e pronto!
    ROW_NUMBER() OVER(PARTITION BY id_maquina ORDER BY data_status DESC) as deduplicacao_primaria,

    -- DENSE_RANK: Pára evitar saltos exóticos na progressão (Ex: Os maiores da loja deram notas: "10, 10, 8", eles ficarão Ranks #1, #1, #2 consecutivo pra não desmotivar). 
    DENSE_RANK() OVER(PARTITION BY id_maquina ORDER BY cpu_mhz DESC) as prioridade_urgencia
FROM server_logs;
```

## Nível Pleno: Running Totals (Acumulados) e Funções Lags
Necessário pra tirar métricas SLAs de Help Desk (Quantos ms eu demorei do etapa 2 pro 5?) e fechar caixas!

```sql
-- Lags (Volta pra linha anterior relacional) / Leads (Acha a Proxima linha do bloco da partição).
SELECT 
    num_chamado, data_emissao as hj,
    LAG(data_emissao) OVER(PARTITION BY num_chamado ORDER BY data_emissao ASC) as emissao_anterior
    -- Você tiraria SLA do gap num: datediff(hj, emissao_anterior)
FROM suporte_ti;

-- Resumos Acumulativos (Year to Date - YTD Sales)
-- P/ ir somando tudo de Tras pra frente no Databricks. A ausência de RANGE impõe "Da Linha atual Ate a Infinidade Anterior Do Bloco".
SELECT 
    mes, receita_mes,
    SUM(receita_mes) OVER(ORDER BY mes) as acumulado_ano_corrente
FROM fechamento;
```

## Sênior (Cluster Health Problem): Range Frames e OOM Errors
A engine exige memória ram bruta pra segurar a janela enquanto lê todas e agrupa. Controlar o volume de blocos define se seu cluster cai ou não.

```sql
-- Moving Average (O range frame MANUAL RESTRITO: Medias Moveis)
SELECT 
    vendedor, venda,
    AVG(venda) OVER (
        PARTITION BY vendedor ORDER BY d_movimento 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW -- SOMA MEU SETOR DOS ULTIMOS 6 DIAS DA SEMANA COM A MINHA LINHA E MEDIA!
    ) AS media_mov_7dias
FROM financeiro;
```
**CRÍTICO DE OOM**: NUNCA UTILIZE CLÁUSULAS GLOBAIS CEGAS NO SPARK (*EX: `AVG(preco) OVER (ORDER BY mes DESC)` * SEM `PARTITION BY`!*). A Ausência ditará que todo mundo no universo cairá pra mesma e uníca pastinha de partição no datalake local do Node0 de Job! A máquina com 16 CPUs tentará varrer de UMA UNICA CPU uma analítica contra toda a sua base bilionária. Use partições (hashes de IDs regionais ou mensais aleatóricas pra subdividir o trabalho aos processadores)!
