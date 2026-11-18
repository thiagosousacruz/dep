# Trilhas (aprofundamento)

Lições de **aprofundamento** de um tema: modelo mental, exemplo para prever, armadilhas e checagem com respostas. O estudo em sequência fica no curso prático ([`../../engenharia_dados`](../../engenharia_dados/README.md)); aqui se chega pela linha "Aprenda o conceito" de cada cheatsheet.

**Rumo:** cada trilha vira matéria-prima de um módulo do curso. Quando o módulo existir, a trilha é apagada, para o mesmo assunto não ficar em dois lugares.

| Camada | Pergunta que responde | Onde |
|---|---|---|
| Trilha | Por que isso existe e como funciona? | `03_trilhas/` → `trilhas.html` |
| Cheatsheet | Qual é a sintaxe e o cuidado? | `01_cheatsheets/` → `cheatsheets.html` |
| Desafio | Consigo fazer sem olhar? | `02_desafios/` → `desafio.html` |

Toda lição segue [o template](../04_templates/template-trilha.md), baseado nos estágios do framework: problema → modelo mental → exemplo para prever → quebre de propósito → erros comuns → checagem → próximos passos.

## Lições

Ordem sugerida, alinhada ao plano de 12 semanas. Cada lição traz o exemplo principal em SQL e em PySpark.

| # | Lição | Semanas | Verificação |
|---|---|---|---|
| 01 | [Ordem lógica do SQL](01_ordem-logica-do-sql.md) | S1 | Spark local |
| 02 | [NULL e lógica de três valores](02_null-e-logica-de-tres-valores.md) | S1, S3 | Spark local |
| 03 | [Grão e cardinalidade](03_grao-e-cardinalidade.md) | S2, S7 | Spark local |
| 04 | [Window functions](04_window-functions.md) | S4, S8 | Spark local |
| 05 | [Como o Spark executa seu código](05_como-o-spark-executa.md) | S6 | Spark local |
| 06 | [Diagnóstico de performance](06_diagnostico-de-performance.md) | S6 | Spark local |
| 07 | [Delta e MERGE idempotente](07_delta-e-merge-idempotente.md) | S5, S7 | lógica em Spark local; `MERGE` e `DESCRIBE HISTORY` a validar no Databricks |
| 08 | [Cargas full, incremental e CDC](08_cargas-incrementais-e-cdc.md) | S9, S10 | lógica em Spark local; `MERGE` e Auto Loader a validar no Databricks |
| 09 | [SCD2 e modelagem dimensional](09_scd2-e-modelagem-dimensional.md) | M9 (12 meses) | staging e join por vigência em Spark local; `MERGE` com `IDENTITY` a validar no Databricks |

Com essas 9 lições, o **núcleo** está completo: todas as skills de SQL, PySpark e Delta do plano de 12 semanas têm trilha. ADF, API/SFTP e orquestração (S9–S10) ficam para a próxima etapa.

## Próximas (fora do núcleo, dependem de Databricks para validar)

- Orquestração e reprocessamento (Workflows, ADF).
- Testes de pipelines PySpark.
- Qualidade de dados e expectations (Lakeflow/DLT).
- Unity Catalog e governança.
- CI/CD com Asset Bundles.
- Observabilidade e custo.

## Regras

- Links para cheatsheets usam o caminho do Markdown com âncora (`../01_cheatsheets/...md#slug`). O build converte e valida.
- Links para desafios usam `../desafio.html?id=<id>`. O build falha se o id não existir.
- Dados sempre fictícios. Aplicação em dados reais só em ambiente autorizado.
