# Performance Tuning e Leitura de Planos

> **Aprenda o conceito:** trilhas [Como o Spark executa seu código](../../03_trilhas/05_como-o-spark-executa.md) · [Diagnóstico de performance](../../03_trilhas/06_diagnostico-de-performance.md) — modelo mental, exemplo para prever e erros comuns.

## Princípio

Otimização começa por evidência: plano físico, métricas da execução, volume lido, shuffle, skew e spill. Evite otimizar apenas pela aparência da consulta.

## Reduzir leitura e transferência

O Catalyst pode aplicar column pruning e predicate pushdown quando a fonte e a expressão permitem. Escrever projeções e filtros claros melhora a intenção, mas confirme no plano se foram efetivamente empurrados para a leitura.

```sql
SELECT id_venda, loja_id, valor
FROM vendas
WHERE data_venda >= DATE '2026-01-01';

EXPLAIN FORMATTED
SELECT id_venda, loja_id, valor
FROM vendas
WHERE data_venda >= DATE '2026-01-01';
```

Procure no plano por filtros na varredura, colunas lidas, exchanges, sorts e estratégia de join. Uma CTE é uma construção lógica; não presuma materialização ou reavaliação sem observar o plano.

## Shuffle, skew e spill

- **Shuffle:** redistribui dados entre executores; é esperado em joins e agregações, mas volume excessivo merece investigação.
- **Skew:** poucas chaves concentram grande parte dos registros, produzindo tarefas muito mais lentas que as demais.
- **Spill:** dados intermediários excedem a memória disponível para a operação e usam disco. Pode ser aceitável; impacto e causa devem ser medidos.

AQE pode coalescer partições pós-shuffle e tratar alguns skew joins. Hints como `BROADCAST` e `REPARTITION` são intervenções: valide o plano antes e depois.

```sql
EXPLAIN FORMATTED
SELECT /*+ BROADCAST(d) */ f.id_venda, d.categoria
FROM fato_vendas AS f
JOIN dim_produto AS d ON f.produto_id = d.produto_id;
```

## Sequência de diagnóstico

1. Confirme resultado, grão e volume esperado.
2. Compare bytes e arquivos lidos com o necessário.
3. Localize exchanges, sorts, joins e agregações mais caros.
4. Compare duração e volume das tarefas para detectar skew.
5. Verifique spill, memória e tamanho das partições.
6. Altere uma variável por vez e meça novamente.

## Checklist

- [ ] Há filtro seletivo e projeção de colunas?
- [ ] O plano confirma pruning e pushdown quando aplicáveis?
- [ ] A estratégia de join é adequada ao tamanho real dos lados?
- [ ] Shuffle, skew e spill foram medidos?
- [ ] A mudança preserva o resultado e melhora uma métrica observável?

