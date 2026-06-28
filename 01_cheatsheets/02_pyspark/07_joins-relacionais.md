# Joins Nativos e Estrategias Dimensionais (PySpark)

## O que e
Processos relacionais entre diferentes conjuntos de particao. Considerado um dos vetores com as mais caras assinaturas em recurso analitico (`Shuffle Bytes`), um Join falho em processamento de grandes lotes corrompe graficos inteiros, consome OOM (Over Memory) e instaura faturas milionarias sem retorno operacional de resultados.

## Nivel Junior/Pleno: Condicionais Multiplos e Ambiguidades
DataFrames em Python carregam chaves que vao chocar com a mesma sintaxe relacional posterior de um cruzamento sem Aliasing. Se voce usar condicoes listadas, o Pyspark trata a dualidade!

```python
# O ARRAY EXPLOSIVO SALVADOR DA AMBIGUIDADE LATENTE (Recomendado)
# Se as duas pontas da tabela vao linkar e O NOME DA CHAVE E IDENTICO NAS DUAS (Ex `id_uf_local`): Declare sempre na lista array. Ele matara silenciosamente a duplicacao gerada pela Tabela Secundaria no Result Frame, evitando select() ambiguo na pipeline final!

df_unificado = df_fato_maestro.join(
    df_dimensao_estado,
    on=["id_uf_local"], 
    how="inner" 
)

# JOINS EM NOME DE CODIGOS DISTINTOS E LOGICAS COMPLEXAS (Variaveis Livres)
# Use Ampersand `&` ou `|` para logicas acirradas.
df_vendas_detalhadas = df_carrinhos.join(
    df_financeiro,
    (df_carrinhos.codigo_barras == df_financeiro.codigo_nf) & 
    (df_carrinhos.data_criacao >= df_financeiro.janela_aprovada),
    "left"
)
```

## O Filtro de Relacao Faltante (Left Anti e Semi Mappings)
Os metodos semi e anti sao a vertente para expurgar analises com sub-queries "Exists ou Nao Exists".

```python
# LEFT ANTI JOIN (Buscador de Gap Relacional Faltante)
# Mostre os pagamentos efetuados mas que Nao constam em nosso target analitico da mao conciliada?
df_vulneraveis = df_pedidos.join(
    df_conciliacao_banco,
    (df_pedidos.id_boleto == df_conciliacao_banco.id_boleto),
    how="left_anti" 
) # Tras todo escopo da Tabela_A porem omitindo cruzamento, apenas filtrando presenças.
```

## Especialista Senior: Hinting Broadcast no Catalyst
A maior e mais fatal amarra performatica e atrelar fatias trilionarias "A" em dicionariozinhos de flag com poucos KBs "B" e induzir Master Workers da Nuvem a fatiar Shuffle Bytes do dicinario inteiro pra todas particicoes rodarem.

```python
from pyspark.sql.functions import broadcast

# O BROADCAST (Pulo Gato das Nuvems): 
# A engine distribui nativamente pela memoria individual das vCPUS as pequenas instrucoes B (Copias Estaticas Limitadas). E as vCPUS entao resolvem a logica isoladas sem trafegar a Fato pelo Fio central dos nodes. Corta duracoes brutais instantaneamente.
df_ultrassonico = df_fato_bilhas.join(
    broadcast(df_dimensao_cores_flags),
    on="codigo_cor_id",
    how="left"
)
# Cuidado: Tabelas de grandes tamanhos receberao Broadcast falho estourando memoria em nodes pequenos (Gargalo Driver Memory Node OufOfMemory).
```
