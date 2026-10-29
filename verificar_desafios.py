"""Executa em Spark local as solucoes dos desafios que trazem dados ficticios.

Opcional: requer pyspark (4.x) e Java. Niveis sem 'dados' ou com "executavel": false
(recursos exclusivos do Databricks, Delta, dbutils) sao pulados.

Uso: python verificar_desafios.py [filtro_de_id]
"""

from __future__ import annotations

import decimal
import json
import os
import re
import sys
from pathlib import Path

os.environ.setdefault("PYSPARK_PYTHON", sys.executable)

from pyspark.sql import SparkSession, Window, functions as F, types as T  # noqa: E402

ROOT = Path(__file__).resolve().parent
TIMEZONE = "America/Sao_Paulo"
TEMPORAL_TYPES = {"DATE", "TIMESTAMP"}


def convert(value, sql_type):
    if value is None or sql_type is None:
        return value
    upper = sql_type.upper()
    if upper.startswith("DECIMAL"):
        return decimal.Decimal(str(value))
    if upper in ("DOUBLE", "FLOAT"):
        return float(value)
    return value


def create_table(spark, table):
    columns, rows, types = table["colunas"], table["linhas"], table.get("tipos")
    if not types:
        return spark.createDataFrame(rows, columns)
    # Datas entram como texto e sao convertidas pelo Spark, no fuso da sessao.
    base = ["STRING" if t.upper() in TEMPORAL_TYPES else t for t in types]
    ddl = ", ".join(f"`{c}` {t}" for c, t in zip(columns, base))
    df = spark.createDataFrame([[convert(v, t) for v, t in zip(row, base)] for row in rows], ddl)
    return df.selectExpr(*[
        f"CAST(`{c}` AS {t}) AS `{c}`" if t.upper() in TEMPORAL_TYPES else f"`{c}`"
        for c, t in zip(columns, types)
    ])


def sql_statements(solution):
    parts = re.split(r";\s*(?:\n|$)", solution)
    return [
        p for p in parts
        if p.strip() and not all(line.strip().startswith("--") for line in p.strip().splitlines())
    ]


def run(spark, challenge, body):
    tables = {t["tabela"]: create_table(spark, t) for t in body["dados"]}
    if challenge["ref"].startswith("01_sql/"):
        for name, df in tables.items():
            df.createOrReplaceTempView(name)
        result = None
        for statement in sql_statements(body["solucao"]):
            result = spark.sql(statement)
        return result.collect() if result is not None else []
    scope = {"spark": spark, "F": F, "T": T, "Window": Window, **tables}
    exec(body["solucao"], scope)
    result = scope.get("resultado")
    return result.collect() if hasattr(result, "collect") else result


def main(id_filter=""):
    spark = (
        SparkSession.builder.master("local[2]")
        .config("spark.ui.enabled", "false")
        .config("spark.ui.showConsoleProgress", "false")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.sql.session.timeZone", TIMEZONE)
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("OFF")
    passed = failed = skipped = 0
    for path in sorted((ROOT / "02_desafios").glob("*.json")):
        for challenge in json.loads(path.read_text(encoding="utf-8")).get("desafios", []):
            if id_filter not in challenge["id"]:
                continue
            for level, body in challenge["niveis"].items():
                if not body.get("dados") or body.get("executavel") is False:
                    skipped += 1
                    continue
                for table in spark.catalog.listTables():
                    if table.isTemporary:
                        spark.catalog.dropTempView(table.name)
                spark.sql("RESET")
                spark.conf.set("spark.sql.session.timeZone", TIMEZONE)
                name = f"{challenge['id']}/{level}"
                try:
                    rows = run(spark, challenge, body)
                    passed += 1
                    print(f"OK   {name}: {str(rows)[:200]}")
                except Exception as error:  # noqa: BLE001 - relatar qualquer falha da solucao
                    failed += 1
                    print(f"FAIL {name}: {str(error).splitlines()[0][:300]}")
    print(f"\nok={passed} falhas={failed} pulados={skipped}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else ""))
