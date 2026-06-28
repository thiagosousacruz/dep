# Modelagem Dimensional e Abordagens Estruturais

## O que e
A modelagem dimensional e a base classica do data warehousing orientado a consumo analitico. Diferente da modelagem transacional, que prioriza integridade operacional e escrita, aqui o foco e facilitar leitura, agregacao, filtros e entendimento para BI e analise.

## 1. Fatos e dimensoes

- **Fato**: registra eventos, movimentos ou metricas de negocio.
- **Dimensao**: registra contexto descritivo para analisar a fato.

Exemplos:
- fato de vendas
- fato de acessos
- dimensao cliente
- dimensao produto
- dimensao calendario

## 2. Abordagens de modelagem

Nao existe modelo universalmente melhor. A escolha depende de:
- volume
- custo de processamento
- custo de armazenamento
- complexidade de consumo
- tipo de BI
- necessidade de reuso entre dominios

### Star Schema
Fato central conectada diretamente a dimensoes mais desnormalizadas.

**Quando usar**
- consumo em BI tradicional
- modelos self-service
- necessidade de simplicidade para o usuario
- cenarios com varias analises por filtros dimensionais

**Vantagens**
- facilita entendimento do modelo
- reduz complexidade de joins para consumo
- costuma funcionar bem em semantic layers e ferramentas de BI

**Trade-offs**
- aumenta redundancia nas dimensoes
- pode repetir atributos textuais em varias estruturas

### Snowflake
Dimensoes mais normalizadas, ligadas a subdimensoes.

**Quando usar**
- dimensoes muito grandes ou muito reutilizadas
- contextos com forte pressao por consistencia e reducao de redundancia
- cenarios onde a semantic layer consegue abstrair parte da complexidade

**Vantagens**
- reduz repeticao de atributos
- melhora organizacao conceitual em alguns dominios

**Trade-offs**
- aumenta complexidade de consumo
- pode piorar usabilidade em BI self-service
- pode adicionar joins e dificultar navegacao do modelo

### OBT (One Big Table)
Fato e atributos dimensionais relevantes sao entregues em uma unica tabela mais achatada.

**Quando usar**
- extracoes especificas e orientadas a um unico caso de uso
- datasets para ciencia de dados
- cenarios onde joins em tempo de consumo sao muito caros ou indesejados

**Vantagens**
- simplifica leitura do consumidor final
- pode reduzir custo de join em runtime

**Trade-offs**
- aumenta redundancia
- dificulta reuso entre diferentes fatos
- deixa manutencao mais cara quando atributos mudam
- pode engessar o modelo se virar padrao para tudo

## 3. Heuristica pratica

- Prefira **star schema** como ponto de partida para BI corporativo.
- Use **snowflake** quando houver ganho real de consistencia ou reducao de redundancia em dimensoes muito pesadas.
- Use **OBT** quando o caso for especifico, orientado a consumo direto e com pouca necessidade de reuso dimensional.

## 4. Sinais de alerta

- Usuario precisa de muitos joins mentais para montar um relatorio simples.
- O mesmo atributo de negocio aparece em varias tabelas com nomes ou significados diferentes.
- O modelo funciona para um dashboard, mas nao se sustenta para analises cruzadas.
- Mudancas pequenas em dimensoes exigem reprocessamento excessivo do modelo.
