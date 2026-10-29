# Backlog de Revisão e Evolução

O núcleo ativo cobre SQL e PySpark. Modeling permanece complementar e streaming, recipes e exercícios estão fora do ciclo atual.

## Concluído nesta consolidação

- [x] Declarar Markdown como fonte de verdade e HTML como artefato gerado.
- [x] Corrigir links para áreas inexistentes ou renomeadas.
- [x] Documentar Modeling como conteúdo complementar fora do build.
- [x] Revisar joins, windows, Catalyst, spill, repartition/coalesce, skew, Pandas UDF e Delta.
- [x] Remover recomendações absolutas e números de performance sem evidência.
- [x] Tornar o build independente do diretório de execução.
- [x] Validar entradas, placeholders, links internos e contagem de seções.
- [x] Preservar a estrutura semântica `pre > code` no HTML.
- [x] Documentar dependências e comando de geração.

## Próximas melhorias

- [ ] Adicionar revisão periódica por versão do Databricks Runtime adotado.
- [ ] Acrescentar referências oficiais nos temas dependentes de versão.
- [ ] Automatizar o build e o verificador de links em CI caso o projeto seja publicado.
- [ ] Expandir exemplos somente a partir de casos reais validados.

## Correções de SQL identificadas (2026-10-28)

Testadas no DBSQL 2026.42 (warehouse serverless).

- [ ] `01_cheatsheets/01_sql/05_ctes.md`: `CACHE VIEW ... AS` não existe (`PARSE_SYNTAX_ERROR`). A sintaxe é `CACHE TABLE nome AS SELECT`. Confirmar se o warehouse serverless executa o comando.
- [ ] `05_ctes.md` × `12_performance-tuning.md`: o 05 afirma que uma CTE referenciada N vezes é lida N vezes; o 12 orienta a não presumir materialização ou reavaliação sem olhar o plano. Alinhar o 05 ao 12 (o plano pode reaproveitar a leitura, com `ReusedExchange`).
- [ ] `06_group-by-e-pivots.md`: `approx_count_distinct` citado com "2% taxa de erro". O padrão é `relativeSD = 0.05` (5%), ajustável pelo 2º argumento.
- [ ] `01_sintaxe-basica.md`: a ordem de execução omite janelas/`QUALIFY` e `DISTINCT`.
- [ ] `IFF` em `04_nulos-e-condicionais.md`, `05_ctes.md` e `11_data-quality-profiling.md`: funciona no Databricks, mas é específico dele. Considerar `if()` ou `CASE`, ou avisar que não é portável.

