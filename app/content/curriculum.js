// ============================================================
// GRAFO DE CONHECIMENTO (DAG) — BILÍNGUE SQL + PYSPARK
// ============================================================
// Curadoria Modular de Conteúdo: Todas as questões, templates e estrutura
// do mapa de evolução ficam separadas da engine principal.

window.KNOWLEDGE_GRAPH = {
  // ═══════════════════ CAMADA 0: Fundações ═══════════════════
  sql_select: {
    id: "sql_select", name: "SELECT Básico", type: "sql",
    prereqs: [], x: 250, y: 60,
    concepts: [
      { concept_id: "select_star", name: "SELECT * (projeção completa)", questions: [
        { template: "Escreva uma query que retorne TODAS as colunas da tabela '<strong>{tabela}</strong>'.",
          gabarito_template: "SELECT * FROM {tabela}", parameters: { tabela: ["vendas", "clientes", "produtos"] }, enforce_order: false, tempo: 20 },
        { template: "Inspecione os dados originais trazendo tudo da tabela '<strong>{tabela}</strong>'.",
          gabarito_template: "SELECT * FROM {tabela}", parameters: { tabela: ["vendas", "clientes"] }, enforce_order: false, tempo: 20 }
      ]},
      { concept_id: "select_cols", name: "SELECT colunas específicas", questions: [
        { template: "Projete apenas '<strong>{col1}</strong>' e '<strong>{col2}</strong>' da tabela '<strong>clientes</strong>'.",
          gabarito_template: "SELECT {col1}, {col2} FROM clientes", parameters: { col1: ["id_cliente", "nome"], col2: ["email", "pais"] }, enforce_order: false, tempo: 25 },
        { template: "Projete '<strong>id_venda</strong>', '<strong>valor</strong>' e '<strong>regiao</strong>' da tabela '<strong>vendas</strong>'.",
          gabarito_template: "SELECT id_venda, valor, regiao FROM vendas", parameters: {}, enforce_order: false, tempo: 25 },
        { template: "Recupere o '<strong>nome_produto</strong>' e o '<strong>preco_unitario</strong>' da tabela '<strong>produtos</strong>'.",
          gabarito_template: "SELECT nome_produto, preco_unitario FROM produtos", parameters: {}, enforce_order: false, tempo: 25 }
      ]},
      { concept_id: "select_alias", name: "SELECT com Aliases (AS)", questions: [
        { template: "Selecione '<strong>id_produto</strong>' renomeada para '<strong>codigo</strong>' e '<strong>nome_produto</strong>' renomeada para '<strong>descricao</strong>' da tabela '<strong>produtos</strong>'.",
          gabarito_template: "SELECT id_produto AS codigo, nome_produto AS descricao FROM produtos", parameters: {}, enforce_order: false, tempo: 30 },
        { template: "Selecione '<strong>nome</strong>' como '<strong>{alias1}</strong>' e '<strong>pais</strong>' como '<strong>{alias2}</strong>' da tabela '<strong>clientes</strong>'.",
          gabarito_template: "SELECT nome AS {alias1}, pais AS {alias2} FROM clientes", parameters: { alias1: ["nome_cliente", "cliente_nome"], alias2: ["pais_origem", "nacionalidade"] }, enforce_order: false, tempo: 30 }
      ]}
    ],
    review: { mix_from: ["select_star", "select_cols", "select_alias"], count: 3 }
  },

  spk_select: {
    id: "spk_select", name: "PySpark: select", type: "pyspark",
    prereqs: ["sql_select"], x: 700, y: 60,
    concepts: [
      { concept_id: "spark_read_select", name: "read.json + select", questions: [
        { template: "Carregue '<strong>{tabela}</strong>' e crie '<strong>result</strong>' selecionando '<strong>{col1}</strong>' e '<strong>{col2}</strong>'.",
          gabarito_template: "df = spark.read.json('{tabela}')\nresult = df.select('{col1}', '{col2}')", parameters: { tabela: ["vendas"], col1: ["id_venda", "valor"], col2: ["regiao", "status"] }, enforce_order: false, tempo: 40 },
        { template: "Carregue '<strong>clientes</strong>' e selecione '<strong>nome</strong>' e '<strong>email</strong>' no DataFrame final '<strong>result</strong>'.",
          gabarito_template: "df = spark.read.json('clientes')\nresult = df.select('nome', 'email')", parameters: {}, enforce_order: false, tempo: 35 }
      ]},
      { concept_id: "spark_alias", name: "select com alias", questions: [
        { template: "De '<strong>produtos</strong>', selecione '<strong>id_produto</strong>' como '<strong>{alias1}</strong>' e '<strong>nome_produto</strong>' como '<strong>descricao</strong>'. Salve em '<strong>result</strong>'.",
          gabarito_template: "df = spark.read.json('produtos')\nresult = df.select(col('id_produto').alias('{alias1}'), col('nome_produto').alias('descricao'))", parameters: { alias1: ["codigo", "id"] }, enforce_order: false, tempo: 55 },
        { template: "De '<strong>vendas</strong>', selecione '<strong>valor</strong>' como '<strong>receita</strong>'. Salve em '<strong>result</strong>'.",
          gabarito_template: "df = spark.read.json('vendas')\nresult = df.select(col('valor').alias('receita'))", parameters: {}, enforce_order: false, tempo: 40 }
      ]}
    ],
    review: { mix_from: ["spark_read_select", "spark_alias"], count: 3 }
  },

  // ═══════════════════ CAMADA 1: Filtros ═══════════════════
  sql_where: {
    id: "sql_where", name: "WHERE Filtros", type: "sql",
    prereqs: ["sql_select"], x: 250, y: 170,
    concepts: [
      { concept_id: "where_equal", name: "WHERE com igualdade (=)", questions: [
        { template: "Projete '<strong>id_cliente</strong>' e '<strong>nome</strong>' de '<strong>clientes</strong>' filtrando onde o país seja '<strong>{pais}</strong>'.",
          gabarito_template: "SELECT id_cliente, nome FROM clientes WHERE pais = '{pais}'", parameters: { pais: ["Brasil", "Portugal", "Angola"] }, enforce_order: false, tempo: 35 },
        { template: "Selecione tudo de '<strong>vendas</strong>' onde a região seja '<strong>{regiao}</strong>'.",
          gabarito_template: "SELECT * FROM vendas WHERE regiao = '{regiao}'", parameters: { regiao: ["Sul", "Norte", "Nordeste"] }, enforce_order: false, tempo: 30 }
      ]},
      { concept_id: "where_comparison", name: "WHERE com comparação (>, <)", questions: [
        { template: "Selecione '<strong>nome_produto</strong>' e '<strong>preco_unitario</strong>' de '<strong>produtos</strong>' onde o preço unitário seja maior que <strong>{preco}</strong>.",
          gabarito_template: "SELECT nome_produto, preco_unitario FROM produtos WHERE preco_unitario > {preco}", parameters: { preco: [100, 500, 1000] }, enforce_order: false, tempo: 35 },
        { template: "Busque todas as colunas de '<strong>vendas</strong>' cuja '<strong>quantidade</strong>' seja menor que <strong>{qtd}</strong>.",
          gabarito_template: "SELECT * FROM vendas WHERE quantidade < {qtd}", parameters: { qtd: [3, 4] }, enforce_order: false, tempo: 35 }
      ]},
      { concept_id: "where_and", name: "WHERE com AND", questions: [
        { template: "Projete '<strong>id_venda</strong>', '<strong>quantidade</strong>' e '<strong>valor</strong>' de '<strong>vendas</strong>' filtrando onde a região seja '<strong>{regiao}</strong>' E a quantidade seja maior que <strong>{qtd}</strong>.",
          gabarito_template: "SELECT id_venda, quantidade, valor FROM vendas WHERE regiao = '{regiao}' AND quantidade > {qtd}", parameters: { regiao: ["Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"], qtd: [1, 2] }, enforce_order: false, tempo: 45 },
        { template: "Encontre clientes de '<strong>{pais}</strong>' que tenham status de assinatura '<strong>{status}</strong>'. Projete todas as colunas.",
          gabarito_template: "SELECT * FROM clientes WHERE pais = '{pais}' AND status_assinatura = '{status}'", parameters: { pais: ["Brasil", "Portugal"], status: ["Ativo", "Inativo"] }, enforce_order: false, tempo: 45 }
      ]}
    ],
    review: { mix_from: ["where_equal", "where_comparison", "where_and"], count: 3 }
  },

  spk_filter: {
    id: "spk_filter", name: "PySpark: filter", type: "pyspark",
    prereqs: ["spk_select", "sql_where"], x: 700, y: 170,
    concepts: [
      { concept_id: "spark_filter_eq", name: "filter com igualdade", questions: [
        { template: "De '<strong>vendas</strong>', selecione '<strong>id_venda</strong>', '<strong>valor</strong>' e '<strong>regiao</strong>' filtrando onde regiao == '<strong>{regiao}</strong>'. Salve em '<strong>result</strong>'.",
          gabarito_template: "df = spark.read.json('vendas')\nresult = df.select('id_venda', 'valor', 'regiao').filter(col('regiao') == '{regiao}')", parameters: { regiao: ["Norte", "Nordeste", "Sudeste", "Sul"] }, enforce_order: false, tempo: 50 },
        { template: "Filtre a tabela '<strong>clientes</strong>' onde status_assinatura == '<strong>{status}</strong>'. Salve em '<strong>result</strong>' mantendo todas as colunas.",
          gabarito_template: "df = spark.read.json('clientes')\nresult = df.filter(col('status_assinatura') == '{status}')", parameters: { status: ["Ativo", "Inativo"] }, enforce_order: false, tempo: 45 }
      ]},
      { concept_id: "spark_withcol_lit", name: "withColumn + lit", questions: [
        { template: "De '<strong>vendas</strong>', selecione '<strong>id_venda</strong>' e '<strong>valor</strong>'. Adicione uma coluna '<strong>moeda</strong>' com o valor literal '<strong>{moeda}</strong>'. Salve em '<strong>result</strong>'.",
          gabarito_template: "df = spark.read.json('vendas')\nresult = df.select('id_venda', 'valor').withColumn('moeda', lit('{moeda}'))", parameters: { moeda: ["BRL", "EUR", "USD"] }, enforce_order: false, tempo: 55 },
        { template: "Carregue '<strong>produtos</strong>'. Adicione uma coluna literal chamada '<strong>desconto</strong>' com valor numérico <strong>{desc}</strong>. Salve em '<strong>result</strong>'.",
          gabarito_template: "df = spark.read.json('produtos')\nresult = df.withColumn('desconto', lit({desc}))", parameters: { desc: [10, 15, 20] }, enforce_order: false, tempo: 50 }
      ]}
    ],
    review: { mix_from: ["spark_filter_eq", "spark_withcol_lit"], count: 3 }
  },

  // ═══════════════════ CAMADA 2: Agregações ═══════════════════
  sql_groupby: {
    id: "sql_groupby", name: "GROUP BY & Agregações", type: "sql",
    prereqs: ["sql_where"], x: 150, y: 290,
    concepts: [
      { concept_id: "count_basic", name: "COUNT(*) básico", questions: [
        { template: "Conte a quantidade de vendas por '<strong>regiao</strong>' na tabela '<strong>vendas</strong>'. Use o alias '<strong>total_vendas</strong>'.",
          gabarito_template: "SELECT regiao, COUNT(*) AS total_vendas FROM vendas GROUP BY regiao", parameters: {}, enforce_order: false, tempo: 40 },
        { template: "Agrupe a tabela '<strong>clientes</strong>' por '<strong>pais</strong>' e conte o total usando o alias '<strong>qtd_clientes</strong>'.",
          gabarito_template: "SELECT pais, COUNT(*) AS qtd_clientes FROM clientes GROUP BY pais", parameters: {}, enforce_order: false, tempo: 40 }
      ]},
      { concept_id: "sum_avg", name: "SUM e AVG", questions: [
        { template: "Calcule a soma total do '<strong>valor</strong>' (alias '<strong>receita_total</strong>') agrupado por '<strong>regiao</strong>' na tabela '<strong>vendas</strong>'.",
          gabarito_template: "SELECT regiao, SUM(valor) AS receita_total FROM vendas GROUP BY regiao", parameters: {}, enforce_order: false, tempo: 45 },
        { template: "Descubra a média ('<strong>AVG</strong>') do '<strong>valor</strong>' agrupado por '<strong>status</strong>' de entrega na tabela '<strong>vendas</strong>'. O alias deve ser '<strong>valor_medio</strong>'.",
          gabarito_template: "SELECT status, AVG(valor) AS valor_medio FROM vendas GROUP BY status", parameters: {}, enforce_order: false, tempo: 50 }
      ]}
    ],
    review: { mix_from: ["count_basic", "sum_avg"], count: 3 }
  },

  sql_join: {
    id: "sql_join", name: "JOINs Relacionais", type: "sql",
    prereqs: ["sql_where"], x: 350, y: 290,
    concepts: [
      { concept_id: "inner_join", name: "INNER JOIN", questions: [
        { template: "Escreva um INNER JOIN entre '<strong>vendas</strong>' e '<strong>clientes</strong>' usando '<strong>id_cliente</strong>'. Projete '<strong>vendas.id_venda</strong>', '<strong>clientes.nome</strong>' e '<strong>vendas.valor</strong>'.",
          gabarito_template: "SELECT vendas.id_venda, clientes.nome, vendas.valor FROM vendas INNER JOIN clientes ON vendas.id_cliente = clientes.id_cliente", parameters: {}, enforce_order: false, tempo: 60 },
        { template: "Faça um INNER JOIN entre '<strong>vendas</strong>' e '<strong>produtos</strong>' por '<strong>id_produto</strong>'. Projete '<strong>vendas.data_venda</strong>' e '<strong>produtos.categoria</strong>'.",
          gabarito_template: "SELECT vendas.data_venda, produtos.categoria FROM vendas INNER JOIN produtos ON vendas.id_produto = produtos.id_produto", parameters: {}, enforce_order: false, tempo: 60 }
      ]},
      { concept_id: "left_join", name: "LEFT JOIN", questions: [
        { template: "Escreva um LEFT JOIN entre '<strong>vendas</strong>' e '<strong>produtos</strong>' usando '<strong>id_produto</strong>'. Projete '<strong>vendas.id_venda</strong>', '<strong>produtos.nome_produto</strong>' e '<strong>vendas.valor</strong>'.",
          gabarito_template: "SELECT vendas.id_venda, produtos.nome_produto, vendas.valor FROM vendas LEFT JOIN produtos ON vendas.id_produto = produtos.id_produto", parameters: {}, enforce_order: false, tempo: 60 },
        { template: "Queremos ver todos os clientes, mesmo que não tenham vendas. Faça um LEFT JOIN de '<strong>clientes</strong>' (tabela da esquerda) com '<strong>vendas</strong>'. Projete '<strong>clientes.nome</strong>' e '<strong>vendas.valor</strong>'.",
          gabarito_template: "SELECT clientes.nome, vendas.valor FROM clientes LEFT JOIN vendas ON clientes.id_cliente = vendas.id_cliente", parameters: {}, enforce_order: false, tempo: 70 }
      ]}
    ],
    review: { mix_from: ["inner_join", "left_join"], count: 3 }
  },

  spk_groupby: {
    id: "spk_groupby", name: "PySpark: groupBy", type: "pyspark",
    prereqs: ["spk_filter"], x: 600, y: 290,
    concepts: [
      { concept_id: "spark_groupby_count", name: "groupBy + count", questions: [
        { template: "De '<strong>vendas</strong>', agrupe por '<strong>regiao</strong>' e conte o número de vendas. Salve em '<strong>result</strong>'.",
          gabarito_template: "df = spark.read.json('vendas')\nresult = df.groupBy('regiao').count()", parameters: {}, enforce_order: false, tempo: 45 },
        { template: "Carregue '<strong>clientes</strong>'. Agrupe por '<strong>status_assinatura</strong>' e conte. Salve em '<strong>result</strong>'.",
          gabarito_template: "df = spark.read.json('clientes')\nresult = df.groupBy('status_assinatura').count()", parameters: {}, enforce_order: false, tempo: 40 }
      ]},
      { concept_id: "spark_groupby_agg", name: "groupBy + agg(sum)", questions: [
        { template: "De '<strong>vendas</strong>', agrupe por '<strong>regiao</strong>' e calcule a soma de '<strong>valor</strong>' com alias '<strong>receita_total</strong>'. Salve em '<strong>result</strong>'.",
          gabarito_template: "df = spark.read.json('vendas')\nresult = df.groupBy('regiao').agg(sum_col('valor').alias('receita_total'))", parameters: {}, enforce_order: false, tempo: 55 },
        { template: "De '<strong>vendas</strong>', agrupe por '<strong>status</strong>' e tire a média ('<strong>avg_col</strong>') do '<strong>valor</strong>' como '<strong>ticket_medio</strong>'. Salve em '<strong>result</strong>'.",
          gabarito_template: "df = spark.read.json('vendas')\nresult = df.groupBy('status').agg(avg_col('valor').alias('ticket_medio'))", parameters: {}, enforce_order: false, tempo: 60 }
      ]}
    ],
    review: { mix_from: ["spark_groupby_count", "spark_groupby_agg"], count: 3 }
  },

  spk_join: {
    id: "spk_join", name: "PySpark: join", type: "pyspark",
    prereqs: ["spk_groupby", "sql_join"], x: 800, y: 290,
    concepts: [
      { concept_id: "spark_inner_join", name: "join inner", questions: [
        { template: "Carregue '<strong>vendas</strong>' e '<strong>clientes</strong>'. Faça um inner join usando '<strong>id_cliente</strong>'. Selecione '<strong>id_venda</strong>' de vendas, '<strong>nome</strong>' de clientes e '<strong>valor</strong>' de vendas. Salve em '<strong>result</strong>'.",
          gabarito_template: "df_v = spark.read.json('vendas')\ndf_c = spark.read.json('clientes')\nresult = df_v.join(df_c, on='id_cliente', how='inner').select('id_venda', 'nome', 'valor')", parameters: {}, enforce_order: false, tempo: 70 },
        { template: "Junte '<strong>vendas</strong>' e '<strong>produtos</strong>' (inner join por '<strong>id_produto</strong>'). Projete '<strong>categoria</strong>' e '<strong>valor</strong>'. Salve em '<strong>result</strong>'.",
          gabarito_template: "df_v = spark.read.json('vendas')\ndf_p = spark.read.json('produtos')\nresult = df_v.join(df_p, on='id_produto', how='inner').select('categoria', 'valor')", parameters: {}, enforce_order: false, tempo: 70 }
      ]},
      { concept_id: "spark_left_join", name: "join left", questions: [
        { template: "Carregue '<strong>vendas</strong>' e '<strong>produtos</strong>'. Faça um left join usando '<strong>id_produto</strong>'. Selecione '<strong>id_venda</strong>', '<strong>nome_produto</strong>' e '<strong>valor</strong>'. Salve em '<strong>result</strong>'.",
          gabarito_template: "df_v = spark.read.json('vendas')\ndf_p = spark.read.json('produtos')\nresult = df_v.join(df_p, on='id_produto', how='left').select('id_venda', 'nome_produto', 'valor')", parameters: {}, enforce_order: false, tempo: 70 },
        { template: "Faça left join de '<strong>clientes</strong>' com '<strong>vendas</strong>' por '<strong>id_cliente</strong>'. Mantenha '<strong>nome</strong>' e '<strong>valor</strong>'. Salve em '<strong>result</strong>'.",
          gabarito_template: "df_c = spark.read.json('clientes')\ndf_v = spark.read.json('vendas')\nresult = df_c.join(df_v, on='id_cliente', how='left').select('nome', 'valor')", parameters: {}, enforce_order: false, tempo: 75 }
      ]}
    ],
    review: { mix_from: ["spark_inner_join", "spark_left_join"], count: 3 }
  },

  // ═══════════════════ CAMADA 3: HAVING e Transformações ═══════════════════
  sql_having: {
    id: "sql_having", name: "HAVING (Filtro pós-agrupamento)", type: "sql",
    prereqs: ["sql_groupby"], x: 150, y: 410,
    concepts: [
      { concept_id: "having_count", name: "HAVING COUNT", questions: [
        { template: "Agrupe '<strong>vendas</strong>' por '<strong>regiao</strong>', conte como '<strong>total</strong>' e filtre (HAVING) apenas regiões com mais de <strong>{n}</strong> vendas.",
          gabarito_template: "SELECT regiao, COUNT(*) AS total FROM vendas GROUP BY regiao HAVING COUNT(*) > {n}", parameters: { n: [3, 5, 6] }, enforce_order: false, tempo: 50 },
        { template: "Agrupe '<strong>clientes</strong>' por '<strong>pais</strong>', conte como '<strong>total_clientes</strong>', mas retorne apenas os países que têm mais de <strong>{x}</strong> clientes.",
          gabarito_template: "SELECT pais, COUNT(*) AS total_clientes FROM clientes GROUP BY pais HAVING COUNT(*) > {x}", parameters: { x: [1, 2, 3] }, enforce_order: false, tempo: 50 }
      ]},
      { concept_id: "having_sum", name: "HAVING SUM", questions: [
        { template: "Agrupe '<strong>vendas</strong>' por '<strong>id_cliente</strong>', calcule '<strong>SUM(valor)</strong>' como '<strong>total_gasto</strong>' e filtre clientes com gasto total maior que <strong>{val}</strong>.",
          gabarito_template: "SELECT id_cliente, SUM(valor) AS total_gasto FROM vendas GROUP BY id_cliente HAVING SUM(valor) > {val}", parameters: { val: [5000, 10000] }, enforce_order: false, tempo: 55 },
        { template: "Agrupe '<strong>vendas</strong>' por '<strong>status</strong>', calcule a soma de valor (alias '<strong>faturamento</strong>') para status com faturamento acima de <strong>{lim}</strong>.",
          gabarito_template: "SELECT status, SUM(valor) AS faturamento FROM vendas GROUP BY status HAVING SUM(valor) > {lim}", parameters: { lim: [20000, 50000] }, enforce_order: false, tempo: 55 }
      ]}
    ],
    review: { mix_from: ["having_count", "having_sum"], count: 3 }
  },

  // ═══════════════════ CAMADA 4: CTEs e Encadeamento ═══════════════════
  sql_cte: {
    id: "sql_cte", name: "CTEs (WITH)", type: "sql",
    prereqs: ["sql_join", "sql_having"], x: 250, y: 520,
    concepts: [
      { concept_id: "cte_basic", name: "CTE básico", questions: [
        { template: "Crie uma CTE '<strong>vendas_grandes</strong>' que selecione '<strong>id_venda</strong>', '<strong>id_cliente</strong>' e '<strong>valor</strong>' de '<strong>vendas</strong>' onde valor > <strong>{val}</strong>. Na query principal, selecione todas as colunas da CTE.",
          gabarito_template: "WITH vendas_grandes AS (SELECT id_venda, id_cliente, valor FROM vendas WHERE valor > {val}) SELECT * FROM vendas_grandes", parameters: { val: [1000, 2000, 5000] }, enforce_order: false, tempo: 60 },
        { template: "Crie CTE '<strong>ativos</strong>' selecionando '<strong>*</strong>' de '<strong>clientes</strong>' onde status_assinatura = '<strong>Ativo</strong>'. Selecione '<strong>nome</strong>' e '<strong>pais</strong>' da CTE.",
          gabarito_template: "WITH ativos AS (SELECT * FROM clientes WHERE status_assinatura = 'Ativo') SELECT nome, pais FROM ativos", parameters: {}, enforce_order: false, tempo: 55 }
      ]},
      { concept_id: "cte_join", name: "CTE com JOIN", questions: [
        { template: "Crie uma CTE '<strong>top_vendas</strong>' com vendas de valor > <strong>1000</strong> (colunas: '<strong>id_venda</strong>', '<strong>id_cliente</strong>', '<strong>valor</strong>'). Na query principal, faça JOIN com '<strong>clientes</strong>' e projete '<strong>clientes.nome</strong>' e '<strong>top_vendas.valor</strong>'.",
          gabarito_template: "WITH top_vendas AS (SELECT id_venda, id_cliente, valor FROM vendas WHERE valor > 1000) SELECT clientes.nome, top_vendas.valor FROM top_vendas INNER JOIN clientes ON top_vendas.id_cliente = clientes.id_cliente", parameters: {}, enforce_order: false, tempo: 75 },
        { template: "CTE '<strong>tech_prods</strong>': selecione '<strong>id_produto</strong>' de '<strong>produtos</strong>' onde categoria = '<strong>Tecnologia</strong>'. Na query, faça INNER JOIN de '<strong>vendas</strong>' com a CTE e selecione '<strong>vendas.valor</strong>'.",
          gabarito_template: "WITH tech_prods AS (SELECT id_produto FROM produtos WHERE categoria = 'Tecnologia') SELECT vendas.valor FROM vendas INNER JOIN tech_prods ON vendas.id_produto = tech_prods.id_produto", parameters: {}, enforce_order: false, tempo: 80 }
      ]}
    ],
    review: { mix_from: ["cte_basic", "cte_join"], count: 3 }
  },

  spk_cte: {
    id: "spk_cte", name: "PySpark: Encadeamento", type: "pyspark",
    prereqs: ["spk_join"], x: 700, y: 520,
    concepts: [
      { concept_id: "spark_chain_filter_select", name: "Encadeamento filter + select", questions: [
        { template: "De '<strong>vendas</strong>', encadeie: filtre valor > <strong>{val}</strong>, e selecione '<strong>id_venda</strong>', '<strong>id_cliente</strong>' e '<strong>valor</strong>'. Salve em '<strong>result</strong>'.",
          gabarito_template: "df = spark.read.json('vendas')\nresult = df.filter(col('valor') > {val}).select('id_venda', 'id_cliente', 'valor')", parameters: { val: [1000, 2000, 5000] }, enforce_order: false, tempo: 50 },
        { template: "Encadeie: carregue '<strong>produtos</strong>', filtre categoria == '<strong>Tecnologia</strong>', selecione '<strong>nome_produto</strong>'. Salve em '<strong>result</strong>'.",
          gabarito_template: "df = spark.read.json('produtos')\nresult = df.filter(col('categoria') == 'Tecnologia').select('nome_produto')", parameters: {}, enforce_order: false, tempo: 45 }
      ]},
      { concept_id: "spark_multi_df", name: "Múltiplos DataFrames + Join", questions: [
        { template: "Crie '<strong>df_v</strong>' (vendas com valor > <strong>1000</strong>) e '<strong>df_c</strong>' (clientes). Faça join de '<strong>df_v</strong>' e '<strong>df_c</strong>' por '<strong>id_cliente</strong>' e selecione '<strong>nome</strong>' e '<strong>valor</strong>'. Salve o dataframe final em '<strong>result</strong>'.",
          gabarito_template: "df_v = spark.read.json('vendas').filter(col('valor') > 1000)\ndf_c = spark.read.json('clientes')\nresult = df_v.join(df_c, on='id_cliente', how='inner').select('nome', 'valor')", parameters: {}, enforce_order: false, tempo: 75 },
        { template: "Crie '<strong>df_p</strong>' (produtos da categoria '<strong>{cat}</strong>'). Faça join com vendas ('<strong>df_v</strong>') usando inner join por '<strong>id_produto</strong>'. Selecione '<strong>id_venda</strong>' e '<strong>valor</strong>'. Salve em '<strong>result</strong>'.",
          gabarito_template: "df_v = spark.read.json('vendas')\ndf_p = spark.read.json('produtos').filter(col('categoria') == '{cat}')\nresult = df_v.join(df_p, on='id_produto', how='inner').select('id_venda', 'valor')", parameters: { cat: ["Tecnologia", "Mobiliário"] }, enforce_order: false, tempo: 80 }
      ]}
    ],
    review: { mix_from: ["spark_chain_filter_select", "spark_multi_df"], count: 3 }
  },

  // ═══════════════════ CAMADA 5: Window Functions ═══════════════════
  sql_window: {
    id: "sql_window", name: "Window Functions", type: "sql",
    prereqs: ["sql_cte"], x: 250, y: 640,
    concepts: [
      { concept_id: "row_number", name: "ROW_NUMBER()", questions: [
        { template: "Selecione '<strong>id_venda</strong>', '<strong>id_cliente</strong>', '<strong>valor</strong>' e crie um '<strong>ROW_NUMBER() OVER (PARTITION BY id_cliente ORDER BY valor DESC)</strong>' como '<strong>rank_venda</strong>' da tabela '<strong>vendas</strong>'.",
          gabarito_template: "SELECT id_venda, id_cliente, valor, ROW_NUMBER() OVER (PARTITION BY id_cliente ORDER BY valor DESC) AS rank_venda FROM vendas", parameters: {}, enforce_order: false, tempo: 75 },
        { template: "Numere as vendas de cada região. Use '<strong>ROW_NUMBER() OVER (PARTITION BY regiao ORDER BY data_venda ASC)</strong>' como '<strong>ordem</strong>', selecionando '<strong>id_venda</strong>' e '<strong>regiao</strong>'.",
          gabarito_template: "SELECT id_venda, regiao, ROW_NUMBER() OVER (PARTITION BY regiao ORDER BY data_venda ASC) AS ordem FROM vendas", parameters: {}, enforce_order: false, tempo: 80 }
      ]},
      { concept_id: "rank_func", name: "RANK()", questions: [
        { template: "Selecione '<strong>id_venda</strong>', '<strong>regiao</strong>', '<strong>valor</strong>' e um '<strong>RANK() OVER (PARTITION BY regiao ORDER BY valor DESC)</strong>' como '<strong>posicao</strong>' da tabela '<strong>vendas</strong>'.",
          gabarito_template: "SELECT id_venda, regiao, valor, RANK() OVER (PARTITION BY regiao ORDER BY valor DESC) AS posicao FROM vendas", parameters: {}, enforce_order: false, tempo: 75 },
        { template: "Crie um ranking global de produtos pelo preço. Selecione '<strong>nome_produto</strong>', '<strong>preco_unitario</strong>' e '<strong>RANK() OVER (ORDER BY preco_unitario DESC)</strong>' como '<strong>top_preco</strong>'.",
          gabarito_template: "SELECT nome_produto, preco_unitario, RANK() OVER (ORDER BY preco_unitario DESC) AS top_preco FROM produtos", parameters: {}, enforce_order: false, tempo: 75 }
      ]}
    ],
    review: { mix_from: ["row_number", "rank_func"], count: 3 }
  },

  spk_window: {
    id: "spk_window", name: "PySpark: Window", type: "pyspark",
    prereqs: ["spk_cte", "sql_window"], x: 700, y: 640,
    concepts: [
      { concept_id: "spark_row_number", name: "row_number() over Window", questions: [
        { template: "Crie um WindowSpec particionado por '<strong>id_cliente</strong>' e ordenado por '<strong>valor</strong>' DESC. Adicione coluna '<strong>rank_venda</strong>' com '<strong>row_number()</strong>'. Selecione '<strong>id_venda</strong>', '<strong>id_cliente</strong>', '<strong>valor</strong>' e '<strong>rank_venda</strong>'. Salve em '<strong>result</strong>'.",
          gabarito_template: "df = spark.read.json('vendas')\nw = Window.partitionBy('id_cliente').orderBy(col('valor').desc())\nresult = df.withColumn('rank_venda', row_number().over(w)).select('id_venda', 'id_cliente', 'valor', 'rank_venda')", parameters: {}, enforce_order: false, tempo: 90 },
        { template: "Particione '<strong>vendas</strong>' por '<strong>regiao</strong>', ordenando por '<strong>data_venda</strong>' crescente. Adicione coluna '<strong>ordem</strong>' (row_number). Selecione '<strong>id_venda</strong>', '<strong>regiao</strong>' e '<strong>ordem</strong>' em '<strong>result</strong>'.",
          gabarito_template: "df = spark.read.json('vendas')\nw = Window.partitionBy('regiao').orderBy('data_venda')\nresult = df.withColumn('ordem', row_number().over(w)).select('id_venda', 'regiao', 'ordem')", parameters: {}, enforce_order: false, tempo: 95 }
      ]},
      { concept_id: "spark_rank", name: "rank() over Window", questions: [
        { template: "Particione por '<strong>regiao</strong>', ordene por '<strong>valor</strong>' DESC. Adicione coluna '<strong>posicao</strong>' com '<strong>rank()</strong>'. Selecione '<strong>id_venda</strong>', '<strong>regiao</strong>', '<strong>valor</strong>' e '<strong>posicao</strong>'. Salve em '<strong>result</strong>'.",
          gabarito_template: "df = spark.read.json('vendas')\nw = Window.partitionBy('regiao').orderBy(col('valor').desc())\nresult = df.withColumn('posicao', rank().over(w)).select('id_venda', 'regiao', 'valor', 'posicao')", parameters: {}, enforce_order: false, tempo: 90 },
        { template: "Crie um ranking global (sem partitionBy) ordenado por '<strong>preco_unitario</strong>' DESC. Adicione coluna '<strong>top_preco</strong>' com '<strong>rank()</strong>'. Selecione '<strong>nome_produto</strong>' e '<strong>top_preco</strong>' de 'produtos'. Salve em '<strong>result</strong>'.",
          gabarito_template: "df = spark.read.json('produtos')\nw = Window.orderBy(col('preco_unitario').desc())\nresult = df.withColumn('top_preco', rank().over(w)).select('nome_produto', 'top_preco')", parameters: {}, enforce_order: false, tempo: 90 }
      ]}
    ],
    review: { mix_from: ["spark_row_number", "spark_rank"], count: 3 }
  }
};

window.GRAPH_EDGES = [
  // SQL path
  ["sql_select", "sql_where"],
  ["sql_where", "sql_groupby"],
  ["sql_where", "sql_join"],
  ["sql_groupby", "sql_having"],
  ["sql_join", "sql_cte"],
  ["sql_having", "sql_cte"],
  ["sql_cte", "sql_window"],
  // PySpark path
  ["sql_select", "spk_select"],
  ["spk_select", "spk_filter"],
  ["sql_where", "spk_filter"],
  ["spk_filter", "spk_groupby"],
  ["spk_groupby", "spk_join"],
  ["sql_join", "spk_join"],
  ["spk_join", "spk_cte"],
  ["spk_cte", "spk_window"],
  ["sql_window", "spk_window"]
];
