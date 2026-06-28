# Databricks Utilities (DbUtils e Automacoes de Ambiente)

## O que e
As extensoes imperativas restritas ao cluster interativo da plataforma Databricks. Atravessam a API DataFrame padrao e concedem interacao base com as camadas arquiteturais da Virtual Machine (Montagem de Discos Databricks File System - DBFS), Cofres Encriptados e Interacoes de Orquestradores Externos em nivel de script (Data Factory Widgets).

## Nivel Junior/Pleno: Manipulacoes Nativas DBFS (Filesystem)
Utilizar importacoes Python legadas de OS (ex: `shutil` e `os`) no ambiente clusterizado pode corromper links virtuais montados se invocados forçosamente. Utilize DbUtils exclusivamente para gestao logistica de midias estaticas.

```python
# EXPANSAO EXPLORATORIA
# Lista metadados e arquivos (retorna uma sublista em objeto iteravel).
pastas_rejeitadas = dbutils.fs.ls("/mnt/silver/lotes_com_falha/")

# MANUSEIO DE DESLOCAMENTOS INTERNOS DE DISCO (Substituindo Shutil)
dbutils.fs.cp("/mnt/silver/relatorio_ontem.csv", "/mnt/silver/bkp/relatorio_ontem.csv")

# HARD DELETE (Saneamento Limpante)
dbutils.fs.rm("/mnt/bronze/logs_estourados_01/", recurse=True) # Destroi a arvore de pastificacao contígua integralmente.
```

## Nivel Senior: DataFactory Bindings & Widgets de Parametrizacao Dinamica
Notebooks sao concebidos como ferramentas de interatividade iterativa isolada. Para orquestrar scripts PySpark repetidas vezes diariamente mudando os alvos contextuais, nao podemos isolar datas manualmente alterando em telas de editor fixo (Hardcoding Constants). As Widgets transportam input externo da malha de automacao direto pro Node da Databricks em run-time.

```python
# DEFINICAO ESPERADA (Container vazio alocador aguardando a injecao via Job/ADF).
dbutils.widgets.text("PARAM_DATACORTE", "2024-01-01", "Label_UI: Data Referencia Lote")
dbutils.widgets.dropdown("PARAM_ENVIRONMENT", "dev", ["dev", "staging", "prod"], "Ambiente Ativo")

# EXTRACAO EM VARIAVEL OPERACIONAL P/ SCRIPT NO CABECALHO (Runtime Getters)
# Orquestrador chamou esse job passando parametro 'prod' e Data '2024-10-18'. O Job internaliza em RunTime!
VAR_AMBIENTE = dbutils.widgets.get("PARAM_ENVIRONMENT")
VAR_LOTE = dbutils.widgets.get("PARAM_DATACORTE")

# Uso em logicas de leitor:
df_alvo_flexivel = spark.read.parquet(f"/mnt/{VAR_AMBIENTE}/cargas_analiticas/data={VAR_LOTE}")
```

## O Cofre Especialista: (Secrets do KeyVault)
Trafego livre e explicito de tokens API em repositorios conectados ao GitHub. Em ambientes profissionais o Azure Key Vault detem os hashes. Você evoca segredos alocados perfeitamente encriptos.

```python
# CHAMADA DE TOKEN NO ESCOPO ATRELO O DATABRICKS AO COFRE:
login_str = dbutils.secrets.get(scope="kv-dbr-prod-scope", key="api-oracle-usuario")
token_str = dbutils.secrets.get(scope="kv-dbr-prod-scope", key="api-oracle-senha")

# SECURITY CHECK:
# A Databricks inibe print explicitos num console aberto de desenvolvedor mutando as strings com os indutores verbais da microsoft "[REDACTED]".

df_externo_oracle = spark.read.jdbc(
    url="jdbc:oracle:thin:@server.corp:1521/XDB",
    table="MASTER_RESTRITO",
    properties={ "user": login_str, "password": token_str } # Input RAM interno limpo de rastros.
)
```
