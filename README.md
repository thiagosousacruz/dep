# Data Engineering Playbook

Base pessoal de consulta rápida para SQL e PySpark em Databricks/Spark, orientada a problemas recorrentes de engenharia de dados.

## Escopo atual

O núcleo mantido e publicado no HTML cobre:

- **SQL:** fundamentos, transformação, Delta Lake, qualidade e performance;
- **PySpark:** DataFrame API, I/O, joins, janelas, schemas, Delta Lake, qualidade e arquitetura.

[`01_cheatsheets/03_modeling-e-analytics/`](01_cheatsheets/03_modeling-e-analytics) permanece como material complementar em Markdown. Essa área não faz parte do build principal e não é prioridade de expansão neste ciclo.

## Como navegar

- [Visão geral de SQL](01_cheatsheets/01_sql/README.md)
- [Visão geral de PySpark](01_cheatsheets/02_pyspark/README.md)
- [Modeling e Analytics — complementar](01_cheatsheets/03_modeling-e-analytics/README.md)
- [Backlog e evolução](06_revisao-evolucao/backlog.md)
- [`cheatsheets.html`](cheatsheets.html), versão navegável gerada de SQL e PySpark

Os arquivos `.md` são a fonte de verdade. O arquivo `cheatsheets.html` é gerado automaticamente e não deve ser editado manualmente.

## Estrutura

- `01_cheatsheets/`: conteúdo técnico reutilizável;
- `04_templates/`: padrão editorial para novos cheatsheets;
- `06_revisao-evolucao/`: avaliações de cobertura e backlog;
- `template.html`: layout, estilos e comportamento do HTML principal;
- `build_docs.py`: gerador e validador do HTML;
- `index.html` e páginas de planos/framework: artefatos independentes, não gerados pelos cheatsheets.

## Gerar o HTML

Requer Python 3.9 ou superior.

```powershell
python -m pip install -r requirements.txt
python build_docs.py
```

O comando pode ser executado de qualquer diretório. Antes de gravar a saída, o gerador valida arquivos de entrada, placeholders, quantidade de seções e links internos.

## Critério de qualidade

O playbook busca ser conciso, tecnicamente seguro e fácil de adaptar. Recomendações sensíveis devem explicar contexto, limites e trade-offs; exemplos dependentes de versão precisam indicar essa dependência.

