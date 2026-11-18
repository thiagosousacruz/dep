# Grão e cardinalidade: por que joins multiplicam linhas

> **Objetivo:** declarar o grão de cada tabela antes de cruzar, prever a cardinalidade de um join e provar com contagens que o resultado não duplicou nem perdeu linhas. **Tempo:** 1–2 h. **Pré-requisitos:** `JOIN`, `GROUP BY` e `COUNT`.

## O problema

A receita do mês sai 37% maior que a do relatório oficial. A consulta "parece certa": um `JOIN` entre vendas e promoções e um `SUM(receita)`. A causa é quase sempre a mesma: uma das tabelas tinha mais de uma linha por chave e o join **replicou** as vendas. Nenhum erro é lançado; só o número fica errado.

## Modelo mental

- **Grão** é a frase "uma linha representa ___". Ex.: *uma linha por venda*, *uma linha por produto por dia*. Se você não consegue completar a frase, não está pronto para cruzar.
- **A chave do grão** é o conjunto de colunas que identifica a linha de forma única. Isso se prova com dados, não se supõe:

```sql
SELECT chave1, chave2, count(*) AS n
FROM tabela
GROUP BY chave1, chave2
HAVING count(*) > 1;   -- vazio = a chave é única
```

- **Cardinalidade do join** depende de quantas linhas cada lado tem *por valor da chave do join*:

```text
esquerda : direita   → linhas por chave no resultado
   1     :    1      → 1               (seguro)
   N     :    1      → N               (mantém o grão da esquerda)
   1     :    N      → N               (muda o grão!)
   N     :    M      → N × M           (exploding join)
```

- **Regra prática:** o lado "de enriquecimento" (dimensão, cadastro, de-para) precisa ser único na chave do join. Se não for, resolva antes: deduplique, filtre a vigência ou agregue.

## Exemplo para prever

```sql
CREATE OR REPLACE TEMP VIEW vendas AS
SELECT * FROM VALUES (1, 'P1', 100), (2, 'P1', 50), (3, 'P2', 80) AS t(id_venda, produto, receita);

CREATE OR REPLACE TEMP VIEW categorias AS
SELECT * FROM VALUES ('P1', 'Calçados'), ('P1', 'Esporte'), ('P2', 'Moda') AS t(produto, categoria);

SELECT count(*) AS linhas, sum(receita) AS receita
FROM vendas v
JOIN categorias c USING (produto);
```

Antes de rodar: quantas linhas e qual a receita? A receita real é 230.

Resultado: **5 linhas e receita 380**. `P1` tem duas categorias, então as vendas 1 e 2 aparecem duas vezes cada (+150). A tabela `categorias` não é única em `produto`: o join é N:M para `P1`.

## Quebre de propósito

1. **Prove a chave.** Rode o teste de unicidade em `categorias` por `produto` e veja `P1` com `n = 2`. Esse teste deveria vir *antes* do join.
2. **Troque para `LEFT JOIN` e acrescente `P3` em vendas** sem categoria. Linhas continuam multiplicadas e agora aparece um `NULL`: left join preserva a esquerda, mas **não** impede duplicação.
3. **Resolva de três jeitos** e compare a receita: (a) escolher uma categoria principal com `row_number()`; (b) agregar as categorias em lista (`collect_set`) antes do join; (c) usar `LEFT SEMI JOIN` quando você só precisa filtrar. Qual responde à pergunta de negócio?
4. **Chave com nulo.** Inclua uma venda com `produto = NULL` e uma categoria com `produto = NULL`. Em `=` elas não se casam (`NULL = NULL` não é verdadeiro); com `<=>` se casam. Decida qual comportamento você quer.
5. **Tipos diferentes.** Mude `produto` para `INT` de um lado e `'001'` do outro. Observe a conversão implícita e linhas que deixam de casar.

## Erros comuns e como diagnosticar

- **Total maior que o esperado** → join replicou. Compare `count(*)` e `count(DISTINCT chave_do_grao)` antes e depois.
- **Total menor que o esperado** → `INNER JOIN` descartou linhas sem correspondência, ou houve nulos e tipos diferentes na chave. Teste com `LEFT ANTI JOIN` para listar o que se perdeu.
- **`DISTINCT` no final para "consertar"** → esconde o sintoma, pode somar errado e custa um shuffle. Corrija o lado não único.
- **SCD2 cruzada sem vigência** → toda versão histórica casa com a venda. Filtre `data_venda` entre `inicio_vigencia` e `fim_vigencia`.

## Cheque seu entendimento

1. Complete: "em `vendas`, uma linha representa ___". Qual é a chave?
2. Por que `LEFT JOIN` não protege contra duplicação?
3. Que consulta prova que uma tabela é única em uma chave?
4. Quais duas contagens você compara para mostrar que um join manteve o grão?
5. Quando `LEFT SEMI JOIN` é melhor que `JOIN` + `DISTINCT`?

## Próximos passos

- **Consulta:** [Cardinalidade e exploding join](../01_cheatsheets/01_sql/07_joins.md#cardinalidade-e-exploding-join) · [Quando usar cada join](../01_cheatsheets/01_sql/07_joins.md#quando-usar) · [Semi e anti join no PySpark](../01_cheatsheets/02_pyspark/07_joins-relacionais.md#semi-e-anti-join)
- **Prática:** [desafio de cardinalidade](../desafio.html?id=sql-07-cardinalidade) · [desafio de tipos de join](../desafio.html?id=sql-07-tipos-de-join) · [desafio de semi e anti join](../desafio.html?id=spk-07-semi-anti)
- **Aplicação real:** escolha uma consulta autorizada que cruze fato e dimensão. Escreva o grão de cada tabela, prove as chaves e registre as contagens antes e depois do join, como pede o critério de avanço da semana 2 do plano.
