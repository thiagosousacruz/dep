# Mapa de skills

Uma linha por skill. Mostra onde cada uma é **aprendida** (trilha), **consultada** (cheatsheet), **praticada** (desafios) e **cobrada** (planos). Atualize ao criar conteúdo novo.

Legenda de status: ✅ ciclo completo (trilha + cheatsheet + desafio) · 🟡 tem referência e prática, falta trilha · 🟠 parcial · ❌ só aparece nos planos.

| Skill | Trilha | Cheatsheet | Desafios | 12 semanas | 12 meses | Status |
|---|---|---|---|---|---|---|
| Sintaxe, filtros e ordem lógica | 01 | SQL 01 | sim | S1 | — | ✅ |
| Agregações e pivots | — | SQL 06 · PySpark 06 | sim | S2, S6 | — | 🟡 |
| Grão, cardinalidade e joins | 03 | SQL 07 · PySpark 07 | sim | S2, S7 | — | ✅ |
| NULL e lógica de três valores | 02 | SQL 04 · PySpark 05 | sim | S1, S3 | — | ✅ |
| CTEs, tipos e condicionais | — (CTEs na 01) | SQL 02–05 · PySpark 03 | sim | S3, S6–7 | M1 | 🟡 |
| Window functions | 04 | SQL 08 · PySpark 08 | sim | S4, S8 | M1 | ✅ |
| Execução do Spark e leitura de plano | 05 | PySpark 01, 13 · SQL 12 | sim | S6 | M2 | ✅ |
| Diagnóstico de performance (skew, spill, AQE) | 06 | SQL 12 · PySpark 13 | sim | S6 | M2, M5 | ✅ |
| JSON, structs e schemas | — | SQL 09 · PySpark 09 | sim | S7 | M1 (schema evolution) | 🟡 |
| Delta, MERGE e idempotência | 07 | SQL 10 · PySpark 10 | sim | S5, S7 | M2, M6 | ✅ (lacunas A no backlog) |
| Leitura e escrita de arquivos | — | PySpark 02 | sim | S7 | — | 🟡 |
| Cargas incrementais e CDC (Auto Loader, CDF) | 08 | — (lacuna A: Auto Loader, CDF) | parcial | S9–S10 | M2 | 🟠 falta cheatsheet |
| Qualidade de dados e profiling | — | SQL 11 · PySpark 12 | sim | S7 | M5, M7 | 🟡 |
| Arquitetura medalhão | — | PySpark 14 | sim | S5 | M1–M2 | 🟡 |
| Modelagem dimensional e SCD2 | 09 | Modeling 01–03 (fora do build) | parcial | — | M9 | 🟠 falta desafio próprio |
| Workspace e `dbutils` | — | PySpark 11 | sim | S10 | — | 🟡 |
| Orquestração e reprocessamento (Workflows, ADF) | — | — | — | S9–S10 | M3, M10 | ❌ |
| Ingestão por API/SFTP e segredos | — | — | — | S10 | — | ❌ |
| Testes de pipelines PySpark | — | PySpark 13 (teste local, parcial) | parcial | — | M5 | 🟠 |
| Unity Catalog e governança | — | — | — | — | M7 | ❌ |
| Lakeflow/DLT e expectations | — | — | — | — | M6 | ❌ |
| CI/CD, Asset Bundles e git | — | — | — | — | M4, M9 | ❌ |
| Observabilidade e custo | — | — | — | — | M5, M10 | ❌ |
| Camada semântica e BI | — | Modeling 04–06 (fora do build) | — | — | M8, M11 | 🟠 |
| Clarificar demanda, validar e comunicar | — | — | — | S11–S12 | M11 | 🟠 (coberto pelo framework) |

## Leitura rápida

- **Núcleo completo:** as 9 trilhas cobrem SQL, PySpark, Delta, cargas incrementais e SCD2. Todas as skills de SQL, PySpark e Delta do plano de 12 semanas têm trilha; ADF, API/SFTP e orquestração (S9–S10) ainda não.
- **Lacunas de referência e prática:** cargas incrementais/CDC não têm cheatsheet (Auto Loader e CDF estão no backlog como prioridade A); SCD2 não tem desafio próprio porque Modeling está fora do build.
- **Ponto cego principal:** orquestração, testes, governança, CI/CD e observabilidade (mês 3 em diante do plano de 12 meses) só aparecem nos planos.
