# Data Engineering Playbook

Base pessoal para aprender, consultar e praticar SQL e PySpark em Databricks/Spark, orientada a problemas recorrentes de engenharia de dados.

| Camada | Para quê | Página |
|---|---|---|
| **Livro** (comece aqui) | Seguir capítulo a capítulo: conceito, exemplo para prever, erros comuns, checagem com respostas e a prática da semana | `trilhas.html` |
| Cheatsheets | Consultar sintaxe e cuidados | `cheatsheets.html` |
| Desafio do Dia | Praticar sem olhar | `desafio.html` |
| Planos e framework | Saber o que estudar e como | `plano-12-semanas.html`, `plano_12_meses_engenheiro_dados.html`, `framework_dominio_tecnico.html` |

## Escopo atual

O núcleo mantido e publicado no HTML cobre:

- **SQL:** fundamentos, transformação, Delta Lake, qualidade e performance;
- **PySpark:** DataFrame API, I/O, joins, janelas, schemas, Delta Lake, qualidade e arquitetura.

[`01_cheatsheets/03_modeling-e-analytics/`](01_cheatsheets/03_modeling-e-analytics) permanece como material complementar em Markdown. Essa área não faz parte do build principal e não é prioridade de expansão neste ciclo.

## Como navegar

- [Livro: capítulos e sumário](03_trilhas/README.md)
- [Mapa de skills](06_revisao-evolucao/mapa-de-skills.md): skill × trilha × cheatsheet × desafio × planos
- [Visão geral de SQL](01_cheatsheets/01_sql/README.md)
- [Visão geral de PySpark](01_cheatsheets/02_pyspark/README.md)
- [Modeling e Analytics — complementar](01_cheatsheets/03_modeling-e-analytics/README.md)
- [Backlog e evolução](06_revisao-evolucao/backlog.md)
- [`cheatsheets.html`](cheatsheets.html), versão navegável gerada de SQL e PySpark
- [`desafio.html`](desafio.html), Desafio do Dia gerado a partir de `02_desafios/`
- [`trilhas.html`](trilhas.html), o livro gerado a partir de `03_trilhas/` (ordem e partes em `03_trilhas/_livro.json`)

Os arquivos `.md` e `02_desafios/*.json` são a fonte de verdade. `cheatsheets.html`, `trilhas.html` e `desafio.html` são gerados automaticamente e não devem ser editados manualmente.

## Desafio do Dia

Todo dia a página sorteia uma seção dos cheatsheets e propõe uma atividade em três níveis (básico, intermediário e avançado). Cada nível traz uma pequena base fictícia ou uma proposta genérica para aplicar na sua base, além de uma solução proposta.

- O sorteio é uma permutação embaralhada por ciclo: todas as seções saem uma vez antes de qualquer repetição, sem favorecer o início dos arquivos. Ele depende só da data, então o desafio é o mesmo em qualquer dispositivo e nada é salvo.
- É possível filtrar por SQL/PySpark e pela semana correspondente do plano de 12 semanas.
- O build falha se uma seção `##` treinável ficar sem desafio. Seções conceituais (O que é, Checklist, Cuidados) e as listadas em `02_desafios/_config.json` ficam de fora.
- As soluções foram escritas para Databricks. As que têm dados fictícios e não dependem de recursos exclusivos (Delta, `dbutils`, `QUALIFY`) podem ser verificadas em Spark local com `python verificar_desafios.py` (opcional; requer `pyspark` 4.x e Java).

## Estrutura

- `01_cheatsheets/`: conteúdo técnico reutilizável;
- `02_desafios/`: banco de desafios (um item por seção treinável) e configuração de semanas;
- `03_trilhas/`: lições conceituais, ligadas aos cheatsheets e desafios;
- `04_templates/`: padrão editorial e checklist de revisão técnica;
- `06_revisao-evolucao/`: avaliações de cobertura, revisões editoriais e backlog;
- `template.html`, `trilhas_template.html` e `desafio_template.html`: layout das páginas geradas;
- `build_docs.py`: gerador e validador dos HTML;
- `verificar_desafios.py`: execução opcional das soluções em Spark local;
- `index.html` e páginas de planos/framework: artefatos independentes, não gerados pelos cheatsheets.

## Gerar o HTML

Requer Python 3.9 ou superior.

```powershell
python -m pip install -r requirements.txt
python build_docs.py
```

O comando pode ser executado de qualquer diretório. Antes de gravar a saída, o gerador valida arquivos de entrada, placeholders, quantidade de seções e links internos. Para os desafios, valida referências às seções, os três níveis, as tabelas de dados e a cobertura. Entre páginas, valida âncoras de outra página, links `desafio.html?id=` e links para Markdown fora do build. Use `python build_docs.py --allow-incomplete` para gerar mesmo com seções novas ainda sem desafio.

## Critério de qualidade

O playbook busca ser conciso, tecnicamente seguro e fácil de adaptar. Recomendações sensíveis devem explicar contexto, limites e trade-offs; exemplos dependentes de versão precisam indicar essa dependência.

