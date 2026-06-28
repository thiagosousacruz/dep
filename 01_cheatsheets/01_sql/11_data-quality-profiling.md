# Profiling Rapido Diario e Checagens de Data Quality (SQL)

## O que e
E a rede de seguranca da pipeline. Nem todo erro de dados derruba o Spark: muitos passam como consulta valida e so aparecem depois em KPI, dashboard ou tabela Gold. O objetivo deste material e mostrar checks curtos e frequentes para validar sanidade antes de publicar dados.

## Checks essenciais de rotina

```sql
-- 1. VERIFICAR SE O GRAO ESPERADO FOI PRESERVADO
-- Use a chave do grao esperado da tabela.
-- Ex.: se a saida deveria ter 1 linha por pedido, compare com id_pedido.
SELECT
    COUNT(1) AS qty_linhas,
    COUNT(DISTINCT id_cliente) AS qty_ids_unicos
FROM tabela_masterizado;

-- 2. VERIFICAR RANGE E REGRAS DE NEGOCIO IMPOSSIVEIS
SELECT
    MIN(idade) AS idade_min,
    MAX(idade) AS idade_max,
    SUM(IFF(valor_bruto < 0, 1, 0)) AS boletos_negativos
FROM db_origem.arquivos_brutos;

-- 3. REPRESENTATIVIDADE E DISTRIBUICAO BASICA
SELECT
    tipo_assinatura,
    COUNT(1) AS base_volumetrica,
    ROUND((COUNT(1) / SUM(COUNT(1)) OVER()) * 100, 2) AS percentual_representatividade
FROM silver_base_contratos
GROUP BY tipo_assinatura;
```

## O que vale conferir antes de publicar
- Grao esperado da tabela.
- Nulos em campos criticos.
- Chaves que deveriam ser unicas.
- Valores fora de range.
- Distribuicao inesperada por categoria.

## Boas praticas
- Compare sempre com a chave correta do grao esperado, nao com qualquer identificador conveniente.
- Execute profiling antes e depois de joins sensiveis.
- Se um `COUNT(DISTINCT ...)` mudar muito, investigue cardinalidade e deduplicacao.
