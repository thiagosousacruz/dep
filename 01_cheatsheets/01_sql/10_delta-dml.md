# Delta Lake: DML, Upserts e Limpezas de Storage (Databricks)

## O que é
Em Data warehouses comuns, `UPDATE` trancava tabelas e derrubava jobs em concorrência, já no sistema Lakehouse open-source *Delta*, os dados são arquivos parquets brutos versionados com `Commit Logs`. Isso permite *Time-Travel* a estados passados e Inserções condencionais via comandos massivos ACID (`Merge Into`).

## Nível Pleno: O UPSERT Seguro (Merge Into)
Seu Job roda todos os dias e extrai a base nova. Inserir a base inteira nos fundos do lago duplica. Deletar a silver antiga primeiro e Gravar dnv onera I/O de rede. O Upsert injeta chaves novas, e Atualiza só as chaves velhas desempadas inteligentemente no Lakehouse sem matar transacoes.

```sql
-- DML Clássico de Upsert Analytics
MERGE INTO master.gold_producao AS target
USING temp.silver_diaria AS source
ON target.id_venda_pk = source.id_venda_pk

-- Chave da Origin casou com do Destino? 
WHEN MATCHED THEN
  -- Pode colocar condicões (So atualize se os valores de preco não forem iguais, senao é perca de ciclo!)
  UPDATE SET 
    target.preco     = source.preco,
    target.data_upd  = current_timestamp()

-- Chave é novissima? 
WHEN NOT MATCHED THEN
  INSERT (id_venda_pk, preco, data_upd)
  VALUES (source.id_venda_pk, source.preco, current_timestamp());
```

## Especialista: Viagem no Tempo (Time Travel) e Compactação de Lixos Físicos Delta
O Delta faz versionamento (tipo Git). A cada Insert, um Log V2 é gerado e o arquivo Parquet V1 velho é orfanado, mas mantido.

```sql
-- TIME TRAVEL: O Analista fez cagada e gravou as 10 da manhã um DROP que sumiu os numéros, acione Restore para a linha mestre versionada de ontém!
SELECT * FROM master.gold_producao TIMESTAMP AS OF '2024-01-01 23:00:00';

RESTORE TABLE master.gold_producao TO TIMESTAMP AS OF '2024-01-01 23:00:00';

-- LIXEIRA (VACCUM) DE BLOCOS: 
-- 30 Dias rodando ETL geram milhares de blocos v1 desativados inuteis. Apague-os Forçadamente do disco cloud para salvar IO limits! (Deleta tudo mais velho q 7 dias do backup history)
VACUUM master.gold_producao RETAIN 168 HOURS;

-- O OPTIMIZE DOS POBRES (Trazendo o Performance Tuning fisico p frente)
-- Aglutina Partições. (O infame problema de mil arquivos zinhos the small file size problem). O Spark abrirá todos os arquivos minúsculos de 10Kb dessa tabela e empacotará eles de 1GB em 1GB contíguos na AWS reduzindo latência no scaner.
OPTIMIZE master.gold_producao ZORDER BY (estado, id_loja); -- Zorder força os clusters mais acionados a grudarem lado a lado.
```
