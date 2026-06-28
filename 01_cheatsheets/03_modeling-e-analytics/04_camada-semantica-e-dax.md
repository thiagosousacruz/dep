# Modelagem de Logicas: Banco SQL vs Camada Semantica

## O que e
Uma das decisoes mais recorrentes em analytics engineering e definir onde cada regra deve viver:
- no SQL ou tabela Gold
- na view semantica
- no modelo de BI
- na medida dinamica

Nao existe resposta unica. A decisao depende da natureza da regra.

## 1. O que tende a ficar no banco ou camada Gold

**Quando faz sentido**
- limpeza e padronizacao
- cast e tratamento de tipos
- regra de negocio estavel
- calculo em nivel de linha
- filtros corporativos universais
- enriquecimento repetido por varios consumidores

**Exemplos**
- `receita_total = quantidade * preco_unitario`
- exclusao de registros logicos deletados
- normalizacao de status
- classificacao fixa de faixas

## 2. O que tende a ficar na camada semantica ou medida

**Quando faz sentido**
- calculo dependente de contexto de filtro
- agregacao dinamica
- comparacoes temporais
- metricas que variam conforme selecao do usuario

**Exemplos**
- ticket medio
- margem percentual
- comparacao ano contra ano
- YTD, MTD, rolling periods

## 3. Heuristica pratica

- Se a regra depende apenas da propria linha e deve valer para toda a empresa, tende a ir para o banco.
- Se a regra depende do contexto do relatorio, tende a ir para a camada semantica.
- Se a mesma metrica precisa ser reutilizada por varios dashboards, vale centralizar em semantic layer governada.

## 4. Riscos comuns

- materializar calculo que deveria ser dinamico
- empurrar para o BI uma regra que deveria ser corporativa e unica
- perder o grao correto da fato tentando entregar "o relatorio pronto" no SQL
- multiplicar logicas duplicadas em varios dashboards
