# Trilhas de aprendizado

Lições para **aprender o conceito**. Os cheatsheets continuam sendo a referência rápida, e o Desafio do Dia continua sendo a prática.

| Camada | Pergunta que responde | Onde |
|---|---|---|
| Trilha | Por que isso existe e como funciona? | `03_trilhas/` → `trilhas.html` |
| Cheatsheet | Qual é a sintaxe e o cuidado? | `01_cheatsheets/` → `cheatsheets.html` |
| Desafio | Consigo fazer sem olhar? | `02_desafios/` → `desafio.html` |

Toda lição segue [o template](../04_templates/template-trilha.md), baseado nos estágios do framework: problema → modelo mental → exemplo para prever → quebre de propósito → erros comuns → checagem → próximos passos.

## Lições

1. [Como o Spark executa seu código](01_como-o-spark-executa.md)
2. [Grão e cardinalidade](02_grao-e-cardinalidade.md)
3. [Window functions](03_window-functions.md)

## Próximas (por prioridade)

- Delta e MERGE idempotente (transação, reexecução, histórico).
- Cargas full, incremental e CDC (watermark, reprocessamento).
- SCD2 e modelagem dimensional.
- Diagnóstico de performance (skew, spill, partições, AQE).

## Regras

- Links para cheatsheets usam o caminho do Markdown com âncora (`../01_cheatsheets/...md#slug`). O build converte e valida.
- Links para desafios usam `../desafio.html?id=<id>`. O build falha se o id não existir.
- Dados sempre fictícios. Aplicação em dados reais só em ambiente autorizado.
