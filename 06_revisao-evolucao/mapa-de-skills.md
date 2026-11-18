# Mapa de skills

Uma linha por skill. Mostra onde cada uma é **aprendida** (trilha), **consultada** (cheatsheet), **praticada** (desafios) e **cobrada** (planos). Atualize ao criar conteúdo novo.

Legenda de status: ✅ ciclo completo (trilha + cheatsheet + desafio) · 🟡 tem referência e prática, falta trilha · 🟠 parcial · ❌ só aparece nos planos.

| Skill | Trilha | Cheatsheet | Desafios | 12 semanas | 12 meses | Status |
|---|---|---|---|---|---|---|
| Sintaxe, filtros e ordenação | — | SQL 01 | sim | S1 | — | 🟡 |
| Agregações e pivots | — | SQL 06 · PySpark 06 | sim | S2, S6 | — | 🟡 |
| Grão, cardinalidade e joins | 02 | SQL 07 · PySpark 07 | sim | S2, S7 | — | ✅ |
| CTEs, tipos, nulos e condicionais | — | SQL 02–05 · PySpark 03, 05 | sim | S3, S6–7 | M1 | 🟡 |
| Window functions | 03 | SQL 08 · PySpark 08 | sim | S4, S8 | M1 | ✅ |
| Execução do Spark e leitura de plano | 01 | PySpark 01, 13 · SQL 12 | sim | S6 | M2 | ✅ |
| Diagnóstico de performance (skew, spill, AQE) | pendente | SQL 12 · PySpark 13 | sim | S6 | M2, M5 | 🟡 |
| JSON, structs e schemas | — | SQL 09 · PySpark 09 | sim | S7 | M1 (schema evolution) | 🟡 |
| Delta, MERGE e idempotência | pendente | SQL 10 · PySpark 10 | sim | S5 | M2, M6 | 🟡 (lacunas A no backlog) |
| Leitura e escrita de arquivos | — | PySpark 02 | sim | S7 | — | 🟡 |
| Cargas incrementais e CDC (Auto Loader, CDF) | pendente | — | — | S9 | M2 | ❌ |
| Qualidade de dados e profiling | — | SQL 11 · PySpark 12 | sim | S7 | M5, M7 | 🟡 |
| Arquitetura medalhão | — | PySpark 14 | sim | S5 | M1–M2 | 🟡 |
| Modelagem dimensional e SCD2 | pendente | Modeling 01–03 (fora do build) | — | — | M9 | 🟠 |
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

- **Base de SQL e PySpark:** coberta com referência e prática. Falta transformar em trilha os temas que mais travam (Delta/MERGE, performance).
- **Ponto cego principal:** do plano de 12 semanas a partir da S9 e do plano de 12 meses a partir do M3, quase nada tem material no hub (orquestração, CDC, testes, governança, CI/CD).
- **Próximas trilhas sugeridas:** Delta e MERGE idempotente → Cargas incrementais e CDC → SCD2 → Diagnóstico de performance.
