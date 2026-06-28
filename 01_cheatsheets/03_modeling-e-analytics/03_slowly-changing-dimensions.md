# SCDs: Historizacao de Dimensoes e Chaves Analiticas

## O que e
SCDs definem como atributos de dimensoes mudam ao longo do tempo sem comprometer o consumo analitico. O ponto central e decidir o que precisa preservar historico e o que pode simplesmente ser sobrescrito.

## 1. Chave de negocio vs surrogate key

### Chave de negocio
Identificador vindo da origem operacional.

Exemplos:
- CPF
- CNPJ
- ID do sistema legado

### Surrogate key
Identificador gerado no ambiente analitico para controlar a dimensao.

Exemplos:
- inteiro sequencial
- hash tecnico estavel
- UUID tecnico

**Por que usar surrogate key**
- desacopla a fato da volatilidade da origem
- ajuda a controlar historico
- evita ambiguidade quando a mesma chave de negocio possui multiplas versoes

## 2. Principais tipos

### Tipo 1
Sobrescreve o valor antigo.

**Quando usar**
- correcao sem valor historico
- atributos operacionais sem relevancia analitica historica
- ajustes cosmeticos ou de qualidade

**Risco**
- o passado passa a refletir o valor novo

### Tipo 2
Mantem historico por versao.

**Como funciona**
- fecha a linha antiga
- cria uma nova linha com nova surrogate key
- controla vigencia com data_inicio, data_fim e/ou flag de linha atual

**Quando usar**
- atributos historicamente relevantes para analise
- mudancas de regiao, segmento, status ou classificacao
- necessidade de auditoria temporal

**Pontos criticos**
- diferenciar business key de surrogate key
- controlar vigencia corretamente
- garantir que a fato aponte para a versao valida no tempo do evento

### Tipo 3
Mantem historico limitado em colunas paralelas.

**Quando usar**
- casos simples
- poucas mudancas
- historico curto e controlado

**Limite**
- nao escala bem para multiplas mudancas

## 3. Heuristica de decisao

- Use **tipo 1** quando o historico nao agrega valor analitico.
- Use **tipo 2** quando o atributo muda a interpretacao do passado.
- Use **tipo 3** apenas em casos muito controlados e com baixa necessidade de historico.

## 4. Sinais de alerta

- a dimensao tem varias linhas por business key, mas a fato nao sabe qual versao usar
- a surrogate key existe, mas nao ha vigencia clara
- o atributo muda muito frequentemente e esta inflando a dimensao sem ganho analitico
- o passado do relatorio muda sem aviso apos updates dimensionais
