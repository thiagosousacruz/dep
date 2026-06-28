# Estetica, Ergonomia e Experiencia do Analista Final

## O que e
Um modelo tecnicamente correto ainda pode ser ruim de usar. A ultima milha do analytics engineering e entregar uma camada de consumo clara, segura e amigavel para quem vai explorar os dados.

## 1. Nomenclatura amigavel

Prefira nomes que facam sentido para o usuario final.

**Boas praticas**
- usar nomes claros e orientados ao negocio
- evitar siglas tecnicas obscuras
- padronizar estilo de nomes
- separar nome tecnico interno de nome exibido quando a ferramenta permitir

## 2. Ocultacao de campos tecnicos

Nem tudo que existe no modelo deve aparecer para o usuario.

**Campos que costumam ser ocultados**
- surrogate keys
- foreign keys
- hashes tecnicos
- colunas auxiliares de ETL
- flags temporarias de processamento

**Por que ocultar**
- reduz erro de uso
- melhora experiencia de navegacao
- evita agrupamentos sem sentido

## 3. Hierarquias e navegacao

Quando fizer sentido, entregue estruturas prontas para exploracao.

Exemplos:
- ano > trimestre > mes > dia
- pais > estado > cidade
- categoria > subcategoria > produto

## 4. Heuristica pratica

- exponha o minimo necessario para analise
- esconda o que e tecnico e nao agrega leitura de negocio
- facilite drill-down quando ele for recorrente
- mantenha consistencia entre areas e dashboards

## 5. Sinais de alerta

- usuarios dependem sempre de ajuda para encontrar campos
- ha muitas colunas tecnicas visiveis no modelo
- o mesmo conceito aparece com nomes diferentes
- dashboards quebram porque campos tecnicos foram usados em agregacoes indevidas
