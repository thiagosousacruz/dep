# Tipos de Tabelas Fato e Tipagem de Medidas

## O que e
Definir o grao da fato e uma das decisoes mais importantes do modelo analitico. O tipo da fato determina como a informacao sera carregada, agregada e interpretada no BI.

## 1. Tipos de fato

### Fato transacional
Cada linha representa um evento ou ocorrencia unica.

**Quando usar**
- vendas
- cliques
- pagamentos
- pedidos
- acessos

**Como pensar**
- 1 linha = 1 evento
- normalmente e append-only
- boa para analises de volume, conversao, receita e comportamento

### Snapshot periodico
Cada linha representa o estado de uma entidade em um momento recorrente.

**Quando usar**
- saldo diario
- estoque no fechamento
- quantidade de clientes ativos por dia
- carteira em determinada data

**Como pensar**
- 1 linha = fotografia da entidade em um ponto no tempo
- muito util para analise historica de estado
- exige cuidado com agregacao temporal

### Snapshot acumulativo
Cada linha representa o ciclo de vida de uma entidade ou processo.

**Quando usar**
- funil de vendas
- jornada de pedido
- esteira logistica
- fluxo de chamados

**Como pensar**
- varias datas do processo vivem na mesma linha
- a linha pode sofrer update ao longo do ciclo
- muito util para SLA, lead time e gargalos de processo

## 2. Heuristica de escolha

- Use **transacional** quando o negocio quer analisar eventos.
- Use **snapshot periodico** quando o negocio quer analisar estado ao longo do tempo.
- Use **snapshot acumulativo** quando o negocio quer analisar duracao e passagem por etapas.

## 3. Natureza das medidas

### Aditivas
Podem ser somadas entre as dimensoes, inclusive no tempo.

Exemplos:
- quantidade
- valor faturado
- custo total

### Semi-aditivas
Podem ser somadas em alguns eixos, mas nao ao longo do tempo.

Exemplos:
- saldo bancario
- saldo de estoque
- quantidade em carteira

### Nao aditivas
Nao devem ser somadas diretamente.

Exemplos:
- percentual de margem
- preco medio
- ticket medio
- taxa de conversao

## 4. Sinais de erro de modelagem

- saldo mensal sendo calculado por soma de saldos diarios
- percentual sendo somado como se fosse valor absoluto
- um mesmo processo precisando de updates, mas a fato foi modelada como puramente transacional
- BI exigindo medidas muito complexas para compensar grao mal definido
