# Backlog de Revisao e Evolucao

Registro de problemas identificados, logicas que podem ser melhoradas e pontos falhos na documentacao que precisam ser refeitos ao longo do tempo.

## Duvidas Tecnicas / Backlog
- [ ] Construir cheatsheet sobre particionamento ideal no PySpark (`repartition` vs `coalesce`).
- [x] Completar cheatsheet PySpark com operacoes basicas frequentes de DataFrame API (`selectExpr`, `alias`, `orderBy`, `distinct`, `dropDuplicates`, `unionByName`, `sample`).
- [x] Criar cheatsheet PySpark de data quality operacional (grao, chaves unicas, nulos, comparacao origem vs destino, reconciliacao pos-join).
- [x] Reforcar cobertura de schema enforcement e evolucao em PySpark (`StructType`, `from_json`, `schema_of_json`, colunas opcionais, mudancas de schema).
- [x] Revisar exemplos de timezone em PySpark para evitar conversoes ambiguas de sessao vs UTC.
- [x] Padronizar tecnicamente e editorialmente os cheatsheets de PySpark (estilo, precisao e consistencia).
- [x] Revisar os cheatsheets de `modeling-e-analytics` para reduzir afirmacoes absolutas e incluir trade-offs de decisao.
- [x] Reforcar os cheatsheets de `modeling-e-analytics` com heuristicas praticas de escolha (star vs OBT, snapshot vs transacional, SQL/view vs DAX, quando usar SCD2).
- [x] Melhorar a precisao tecnica da area `modeling-e-analytics` em temas sensiveis como surrogate key, vigencia em SCD2, medidas semi-aditivas e muitos-para-muitos.
- [x] Reestruturar o README de `01_cheatsheets/modeling-e-analytics` para navegacao no GitHub no mesmo padrao de SQL e PySpark.
- [ ] Explorar recipe SQL sobre calculo real de dias uteis utilizando referencias cross join da `Dim_Calendario`.
- [ ] Expandir secao de boas praticas no `joins.md` baseado no uso da Renner.
- [x] Criar cheatsheet SQL sobre tratamento de tipos (`cast`, `try_cast`, `decimal`, `date`, `timestamp`, `boolean`).
- [x] Criar cheatsheet SQL sobre nulos e valores default (`coalesce`, `nullif`, `is null`, string vazia).
- [x] Criar cheatsheet SQL sobre limpeza e padronizacao de strings (`trim`, `upper`, `lower`, `regexp_replace`).
- [x] Criar cheatsheet SQL sobre renomeacao e padronizacao de colunas na camada Silver.
- [x] Criar cheatsheet SQL sobre data quality e profiling rapido para tabelas Silver e Gold.
- [x] Criar recipe SQL para tratamento de nulos.
- [x] Criar recipe SQL para conversao e validacao de tipos.
- [x] Criar recipe SQL para diagnostico de duplicidades e exploding joins.
