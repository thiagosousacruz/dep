# Databricks Utilities (dbutils)

## O que é

`dbutils` é a biblioteca de utilitários dos notebooks e jobs Databricks: manipula arquivos, recebe parâmetros (widgets) e lê segredos. Existe apenas no Databricks; código que depende dele não roda em Spark local sem adaptação.

## Arquivos: dbutils.fs e Volumes

Com Unity Catalog, arquivos não tabulares ficam em **Volumes** (`/Volumes/<catálogo>/<schema>/<volume>/`), com permissões governadas pelo catálogo. Mounts (`/mnt`) e a raiz do DBFS são legado.

```python
arquivos = dbutils.fs.ls("/Volumes/main/silver/arquivos/lotes_com_falha/")
for f in arquivos:
    print(f.name, f.size, f.modificationTime)

dbutils.fs.cp("/Volumes/main/silver/arquivos/relatorio.csv",
              "/Volumes/main/silver/arquivos/bkp/relatorio.csv")

dbutils.fs.rm("/Volumes/main/bronze/arquivos/tmp_carga/", recurse=True)   # irreversível
```

- Volumes também aceitam APIs locais de arquivo (`open`, `os`, `shutil`) no caminho `/Volumes/...`.
- `rm` com `recurse=True` apaga sem lixeira: confira o caminho (de preferência parametrizado e validado) antes.
- Nunca apague com `dbutils.fs.rm` arquivos dentro do diretório de uma tabela Delta; use `DELETE`/`VACUUM`.

## Parâmetros: widgets e job parameters

Widgets recebem valores do usuário no notebook ou de parâmetros do job, evitando datas e ambientes fixos no código.

```python
from pyspark.sql import functions as F

dbutils.widgets.text("data_corte", "2025-01-01", "Data de corte")
dbutils.widgets.dropdown("ambiente", "dev", ["dev", "hml", "prod"], "Ambiente")

ambiente = dbutils.widgets.get("ambiente")
data_corte = dbutils.widgets.get("data_corte")

df = spark.read.table(f"{ambiente}.silver.cargas").filter(F.col("dt_carga") == data_corte)
```

- O valor sempre chega como string: converta e valide (`datetime.date.fromisoformat(data_corte)`).
- Em jobs, parâmetros do job e de tarefa preenchem os widgets de mesmo nome.

## Segredos

Credenciais ficam em secret scopes (gerenciados pelo Databricks ou ligados a Azure Key Vault), nunca no código ou no repositório.

```python
usuario = dbutils.secrets.get(scope="erp-prod", key="usuario")
senha = dbutils.secrets.get(scope="erp-prod", key="senha")

df_erp = spark.read.jdbc(
    url="jdbc:oracle:thin:@servidor:1521/XDB",
    table="VENDAS",
    properties={"user": usuario, "password": senha},
)
```

- O notebook mostra `[REDACTED]` ao imprimir um segredo, mas isso não é proteção completa: transformar o valor (ex.: imprimir caractere por caractere) o expõe. Controle quem pode ler o scope.
- `dbutils.secrets.list("erp-prod")` lista chaves sem revelar valores.

## Checklist

- [ ] Caminhos usam Volumes do Unity Catalog em vez de `/mnt`?
- [ ] Parâmetros são convertidos e validados?
- [ ] Nenhuma credencial aparece no código?
- [ ] Operações destrutivas usam caminho validado?
