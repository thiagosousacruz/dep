# Medalhao: Bronze, Silver e Gold no Databricks

## O que e
A arquitetura medalhao organiza os dados em camadas com papeis diferentes ao longo do pipeline. Ela ajuda a separar ingestao, confiabilidade estrutural e consumo analitico, reduzindo acoplamento e melhorando rastreabilidade.

No contexto Databricks, essa separacao tambem ajuda a decidir:
- onde aplicar limpeza
- onde tipar
- onde deduplicar
- onde enriquecer
- onde agregar
- onde expor para BI ou consumo final

## 1. Papel de cada camada

### Bronze
Camada mais proxima da origem.

**Objetivo**
- preservar o dado ingerido
- manter rastreabilidade
- registrar contexto de carga

**O que normalmente entra aqui**
- dados crus ou quase crus
- schema proximo da origem
- arquivos, tabelas ou streams ingeridos
- metadados tecnicos de ingestao

**O que evitar**
- regras de negocio pesadas
- limpeza destrutiva
- agregacoes
- joins de consumo

### Silver
Camada de confiabilidade estrutural.

**Objetivo**
- transformar o dado cru em dado utilizavel
- corrigir tipos
- tratar nulos e padroes
- deduplicar quando necessario
- padronizar chaves e nomes

**O que normalmente entra aqui**
- entidades limpas
- eventos confiaveis
- tabelas com schema estabilizado
- regras de qualidade e enriquecimento leve

**O que evitar**
- tabelas excessivamente agregadas
- metricas de dashboard especificas
- logicas altamente dependentes de um unico consumidor

### Gold
Camada de consumo.

**Objetivo**
- entregar dados prontos para analise
- organizar marts, fatos, dimensoes e tabelas analiticas
- otimizar acesso de BI, analytics e consumo de negocio

**O que normalmente entra aqui**
- tabelas fato
- dimensoes
- tabelas agregadas
- visoes de negocio
- datasets finais para dashboard

**O que evitar**
- virar deposito de toda regra da empresa sem criterio
- duplicar muitas versoes do mesmo dataset sem necessidade
- carregar complexidade tecnica que deveria ter sido resolvida na Silver

## 2. Como pensar granularidade

Granularidade deve ficar clara em cada camada.

### Bronze
- normalmente segue o grao da origem
- 1 linha pode significar 1 evento cru, 1 registro operacional ou 1 documento ingerido

### Silver
- deve representar um grao confiavel e estavel
- 1 linha precisa ter significado claro para engenharia e consumo intermediario
- deduplicacao e padronizacao costumam acontecer aqui

### Gold
- o grao deve refletir o caso de uso analitico
- pode ser transacional, snapshot, acumulativo ou agregado
- precisa estar explicito para evitar KPI errado

## 3. O que costuma ser feito em cada camada

### Bronze
- ingestao de arquivos/tabelas
- captura de metadados de carga
- particionamento tecnico de aterrissagem quando fizer sentido
- armazenamento do dado bruto

### Silver
- cast e tipagem
- tratamento de nulos
- limpeza de strings
- padronizacao de nomes
- deduplicacao
- validacao de chaves
- enriquecimento leve
- conformacao entre fontes

### Gold
- joins orientados a consumo
- modelagem dimensional
- regras de negocio consolidadas
- agregacoes e marts
- semanticas de indicadores
- tabelas finais para BI, analytics e reporting

## 4. Colunas tecnicas uteis

Nem toda coluna tecnica precisa existir em toda camada, mas estas sao comuns:

- `ingestion_ts`
- `load_date`
- `source_system`
- `source_file`
- `record_hash`
- `is_current`
- `effective_start_date`
- `effective_end_date`
- `update_ts`

### Heuristica
- Bronze: priorize rastreabilidade
- Silver: priorize confiabilidade e controle
- Gold: mantenha apenas o que ajuda consumo, auditoria ou historizacao

## 5. Regras praticas de qualidade por camada

### Bronze
- o dado chegou?
- chegou completo?
- a origem foi identificada?

### Silver
- tipos estao corretos?
- nulos criticos foram tratados?
- o grao esta consistente?
- ha duplicidades indevidas?

### Gold
- a semantica do indicador esta correta?
- o join preserva a cardinalidade esperada?
- o dataset final esta pronto para consumo sem ambiguidade?

## 6. Erros comuns

- fazer limpeza destrutiva na Bronze
- pular a Silver e transformar a Bronze direto em dataset final
- colocar regra de dashboard na Silver
- agregar cedo demais e perder flexibilidade analitica
- deixar Gold com cara de camada tecnica, e nao de consumo
- nao explicitar o grao final da tabela

## 7. Heuristica de decisao rapida

- Se a tabela existe para preservar a origem: Bronze
- Se a tabela existe para tornar o dado confiavel e reutilizavel: Silver
- Se a tabela existe para analise, KPI ou BI: Gold

## 8. Relacao com outros cheatsheets

Este material conversa diretamente com:

- [`02_leitura-escrita-io.md`](02_leitura-escrita-io.md)
- [`03_exploracao-e-tipagem.md`](03_exploracao-e-tipagem.md)
- [`04_transformacoes-e-df-api.md`](04_transformacoes-e-df-api.md)
- [`05_nulos-e-condicionais.md`](05_nulos-e-condicionais.md)
- [`10_delta-lake-api.md`](10_delta-lake-api.md)
- [`12_data-quality-operacional.md`](12_data-quality-operacional.md)
- [`13_performance-e-arquitetura.md`](13_performance-e-arquitetura.md)
