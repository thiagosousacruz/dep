# Performance Tuning e Leitura de Planos (Spark Engine)

## O que é
Enquanto um analista se contenta que a "*query funciona*", o Engenheiro de Dados certifica-se de que a query "*Custa centavos para rodar no Cluster Distribuído e não falhará à meia-noite em cenários de alta escabilidade*". É a refatoração do código SQL usando as alavancas lógicas para burlar o envio de massas brutas pela rede do cluster (Shuffling inter-nodes).

## Nível Pleno: Leituras Direcionais e PushDowns
Não traga lixo para o interpretador de plano! O Catalyst SQL do Spark lê a pipeline de final para início e se encontra defasagens de colunas inúteis pedidas nas `CTES` iniciais que ele nem vai cruzar na saída do Dashboard, ele força varredura nelas mesmo assim onerando redes. Filtre nas Pontas do `FROM`. E prefira partições físicas sempre (`Date >= ... `).

```sql
-- ERRO DO JUNINHO! Leu de 2010 a 2024 de um datalake de 4 terabytes na CTE só pra filtrar por data no Master SELECT? O cluster travará caindo tudo na memoria atoa primeiro.
WITH X AS (SELECT * FROM gigantesca_df ), Y AS (...)
SELECT * FROM X JOIN Y WHERE X.date > '2024';

-- O JEITO SÉRIO PREVENTIVO: Predicate Pushdown! Use as chaves Preditivas atreladas a Pastas já nos primeirs FROMs.
WITH X AS (
    SELECT id, total FROM gigantesca_df 
    WHERE year_partition >= 2024 -- A engine pula a leitura em disco das pastas passadas do StorageS3.
) ...
```

## Sênior (Especialistas Nuvens DBR): Adaptive Query Execution e Spillings
*O Pior erro Pós OOM (Out Of Memory Error): O Spilling In-Disks!*
Significa que uma máquina não agentou a memoria cruzada de Tabela A com Tabela B, e ela começou a Descer (Spillar) partes da Tabela para a memória SDD e Disco Rígido para forçar a query a caber. Como os cabos do disco são infinitamente mais vagarosos que a RAM C++, seu Pipeline Spark atrasará cerca de **5 a 10 horas rotineiramente**.

```sql
-- DICA 1: Tabela tá derramando para disco? Balanceio Particional (Evitando a assimetria maldita do Skew Data num worker solteiro)!
-- O Repartition redistribui cegamente forçando shuffles os dados da matriz, se a Chave X tiver muitos repetidos, todos iriam pra 1 processador, mande pelo gerador aleatório.
SELECT /*+ REPARTITION(200) */ a.id, a.nome 
FROM banco_estourado a;

-- DICA 2: FORCE A LEITURA DO PLANO DE VOOS (EXPLAIN)
-- Antes de injetar o script na Pipeline. Cheque seu destino e alocacoes.
EXPLAIN EXTENDED 
SELECT a.id, b.status FROM A INNER JOIN B... -- Mostra a árvore Physical plan lida de Tras p Frete do Catalyst sobre os Shuffles!
```
