# Otimizacao Funcional e Estresse de Consumo Analitico

## O que e
Uma boa modelagem analitica nao depende apenas da engenharia de dados. O modo de consumo no BI tambem afeta custo, latencia, limites de uso e experiencia final.

## 1. Importacao vs consulta direta

### Import Mode
Os dados sao carregados para o motor do BI.

**Quando usar**
- dashboards com alta interatividade
- modelos com uso intenso de medidas
- cenarios em que refresh por agenda e suficiente

**Vantagens**
- melhor performance de consumo
- boa experiencia para navegacao e exploracao

**Trade-offs**
- depende de refresh
- limitado por capacidade/licenciamento
- menos adequado para necessidade de tempo quase real

### DirectQuery ou consulta direta
O BI consulta a origem a cada interacao relevante.

**Quando usar**
- necessidade de dado mais atual
- volume que nao cabe bem em importacao
- estrategia de consumo fortemente apoiada na origem

**Vantagens**
- menor dependencia de refresh completo
- pode escalar melhor em cenarios de dados muito grandes

**Trade-offs**
- experiencia mais sensivel a latencia da origem
- mais dependencia da performance do warehouse/lakehouse
- algumas funcoes e modelagens podem ficar mais restritas

## 2. Relacoes complexas

Relacoes muitos-para-muitos e filtros bidirecionais exigem cuidado.

**Quando sao um risco**
- multiplos caminhos de filtro
- fatos diferentes ligadas de forma ambigua
- loops de relacionamento
- resultados inconsistentes entre visuais

**Boas praticas**
- preferir modelo em estrela
- evitar bidirecional sem necessidade clara
- usar tabelas ponte quando necessario
- validar cardinalidade e direcao de filtro

## 3. Sinais de alerta

- visual muda muito de tempo de resposta com pequenos filtros
- total nao bate entre visuais
- mesmo indicador muda dependendo do caminho do filtro
- o modelo exige muitos relacionamentos especiais para funcionar
