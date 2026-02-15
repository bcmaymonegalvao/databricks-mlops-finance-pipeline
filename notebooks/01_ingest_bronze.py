# Databricks notebook source
# MAGIC %md
# MAGIC # 01 — Ingest → Bronze (placeholder)
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC # 01 — Ingest → Bronze (PTAX USD via BCB OData)
# MAGIC
# MAGIC Fixes:
# MAGIC - Avoids Spark schema inference on empty datasets (explicit schema)
# MAGIC - Corrects BCB OData function signature/params for CotacaoDolarPeriodo
# MAGIC - Fixes typo in ptax_sell casting
# MAGIC - Improves first-run behavior (creates schema/table safely)
# MAGIC - Adds lightweight request/row-count logging

# COMMAND ----------

# MAGIC %md
# MAGIC ## Nota de design (conforme documentação do projeto)
# MAGIC - **Bronze** deve armazenar dados **raw / append-only** (sem deduplicar por dia).
# MAGIC - O endpoint `CotacaoDolarPeriodo` **não possui** a coluna `tipoBoletim`; portanto, Bronze não filtra/seleciona por isso.
# MAGIC - Deduplicação por `ds` (1 registro por dia) e regras de qualidade ficam para o **Notebook 02 (Silver)**.
# MAGIC - Chave técnica de idempotência no Bronze: `dataHoraCotacao` (evita duplicar cargas com janela sobreposta).


# COMMAND ----------

from __future__ import annotations

import os
from datetime import date, timedelta
from typing import Any

import pandas as pd
import requests
from delta.tables import DeltaTable
from pyspark.sql import functions as F
from pyspark.sql import types as T

# COMMAND ----------

# -----------------------------
# Config (free-friendly)
# -----------------------------

CATALOG       = os.getenv("UC_CATALOG", "").strip()
BRONZE_SCHEMA = os.getenv("BRONZE_SCHEMA", "bronze")
BRONZE_TABLE  = os.getenv("BRONZE_TABLE", "br_fx_ptax_raw")

# Janela padrão (primeira carga): últimos N dias
DEFAULT_LOOKBACK_DAYS = int(os.getenv("PTAX_LOOKBACK_DAYS", 365))

PTAX_BASE             = "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata"
PTAX_RESOURCE         = "CotacaoDolarPeriodo"  # recurso de período do dolar (PTAX)

# OData pagination
PTAX_TOP = int(os.getenv("PTAX_TOP", 10000))

# COMMAND ----------

# DBTITLE 1,Fix SyntaxError in bcb_date function
def fq(schema: str, table: str) -> str:
    """Fully qualified table name, with optional Unity Catalog."""
    return f"{CATALOG}.{schema}.{table}" if CATALOG else f"{schema}.{table}"

def schema_fq(schema: str) -> str:
    return f"{CATALOG}.{schema}" if CATALOG else schema


def bcb_date(d: date) -> str:
    """BCB OData expects 'MM-DD-YYYY' wrapped in single quotes."""
    return f"'{d.strftime('%m-%d-%Y')}'"


def table_exists(name: str) -> bool:
    try:
        spark.table(name)  # type: ignore[name-defined]
        return True
    except Exception:
        return False

# COMMAND ----------

BRONZE_SPARK_SCHEMA = T.StructType(
    [
        T.StructField("ds", T.DateType(), True),  # derivado de dataHoraCotacao, útil p/ particionar/consultar
        T.StructField("dataHoraCotacao", T.TimestampType(), True),
        T.StructField("cotacaoCompra", T.DoubleType(), True),
        T.StructField("cotacaoVenda", T.DoubleType(), True),
        T.StructField("source", T.StringType(), True),
        T.StructField("ingestion_ts", T.TimestampType(), True),
    ]
)


# COMMAND ----------

# DBTITLE 1,Fix SyntaxError in get_incremental_window
def get_incremental_window(target_table: str) -> tuple[date, date]:
    """
    Estratégia incremental:
    - Se a table existe: Volta 7 dias (buffer) a partir do max(ds)
    - senão: usa DEFAULT_LOOKBACK_DAYS
    """
    today = date.today()
    end = today
    if table_exists(target_table):
        max_ds = (
            spark.table(target_table)
            .select(F.max("ds").alias("max_ds"))
            .collect()[0]["max_ds"]
        )
        if max_ds is None:
            start = end - timedelta(days=DEFAULT_LOOKBACK_DAYS)
        else:
            start = (max_ds - timedelta(days=7))
    else:
        start = end - timedelta(days=DEFAULT_LOOKBACK_DAYS)
    # Cap end date to today
    if end > today:
        end = today
    return start, end

# COMMAND ----------

from datetime import date, timedelta

end = date.today()

def last_business_day(d: date) -> date:
    while d.weekday() >= 5:  # 5=sáb, 6=dom
        d -= timedelta(days=1)
    return d

safe_end = last_business_day(min(end, date.today() - timedelta(days=1)))


# COMMAND ----------

# DBTITLE 1,Cell 9
def fetch_ptax_period(start: date, end: date, top: int = PTAX_TOP) -> list[dict[str, Any]]:
    """
    Fetch PTAX (USD) by period via BCB OData.
    Uses $skip/$top pagination.
    Filters tipoBoletim='Fechamento' (closing).
    """
    # Signature: (dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)
    endpoint = f"{PTAX_BASE}/{PTAX_RESOURCE}(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)"

    all_rows: list[dict[str, Any]] = []
    skip = 0

    with requests.Session() as s:
        s.headers.update({"User-Agent": "databricks-mlops-finance-pipeline/bronze-ingest"})

        while True:
            params = {
                "@dataInicial": bcb_date(start),
                "@dataFinalCotacao": bcb_date(end),
                "$format": "json",
                "$select": "cotacaoCompra,cotacaoVenda,dataHoraCotacao", # sem  tipoBoletim",
                # "$filter": "tipoBoletim eq 'Fechamento'",
                "$top": str(top),
                "$skip": str(skip),
            }

            r = s.get(endpoint, params=params, timeout=60)
            if r.status_code >= 400:
                print("[PTAX][ERROR]", r.status_code, r.url)
                print((r.text or "")[:2000])
                r.raise_for_status()    

            payload = r.json()
            rows = payload.get("value", [])

            pdf = pd.DataFrame(rows).copy()
            if "tipoBoletim" in pdf.columns:
                pdf = pdf.loc[pdf["tipoBoletim"].astype(str).str.lower().eq("fechamento")]

            # Logging
            if skip == 0:
                print(f"[PTAX] GET {r.url}")
            print(f"[PTAX] page skip={skip} rows={len(rows)}")

            if not rows:
                break

            all_rows.extend(rows)

            if len(rows) < top:
                break
            skip += top

    return all_rows

# COMMAND ----------

def normalize(rows: list[dict[str, Any]]) -> pd.DataFrame:
    cols = ["ds", "dataHoraCotacao", "cotacaoCompra", "cotacaoVenda", "source"]
    if not rows:
        return pd.DataFrame(columns=cols)

    pdf = pd.DataFrame(rows).copy()

    # Tipos
    pdf["dataHoraCotacao"] = pd.to_datetime(pdf["dataHoraCotacao"], errors="coerce")
    pdf["cotacaoCompra"] = pd.to_numeric(pdf["cotacaoCompra"], errors="coerce")
    pdf["cotacaoVenda"]  = pd.to_numeric(pdf["cotacaoVenda"], errors="coerce")

    # ds derivado (não é curadoria; é só uma coluna auxiliar)
    pdf["ds"] = pdf["dataHoraCotacao"].dt.date

    # Lineage
    pdf["source"] = "bcb_ptax"

    # IMPORTANTE: Bronze raw => NÃO deduplicar por ds
    # (Nada de drop_duplicates aqui)

    return pdf[cols]

# COMMAND ----------

def ensure_bronze_objects(target_table: str) -> None:
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {schema_fq(BRONZE_SCHEMA)}")

    spark.sql(f"""
      CREATE TABLE IF NOT EXISTS {target_table} (
        ds DATE,
        dataHoraCotacao TIMESTAMP,
        cotacaoCompra DOUBLE,
        cotacaoVenda DOUBLE,
        source STRING,
        ingestion_ts TIMESTAMP
      )
      USING DELTA
    """)

    print(f"[BRONZE] Ensured schema/table: {target_table}")

# COMMAND ----------

# DBTITLE 1,Cell 8
def upsert_bronze(target_table: str, pdf: pd.DataFrame) -> None:
    ensure_bronze_objects(target_table)

    if pdf.empty:
        print("[BRONZE] No rows to upsert (empty payload after normalize).")
        return

    sdf = spark.createDataFrame(pdf)

    sdf = (
        sdf.withColumn("ds", F.to_date("ds"))
           .withColumn("dataHoraCotacao", F.to_timestamp("dataHoraCotacao"))
           .withColumn("cotacaoCompra", F.col("cotacaoCompra").cast("double"))
           .withColumn("cotacaoVenda",  F.col("cotacaoVenda").cast("double"))
           .withColumn("ingestion_ts", F.current_timestamp())
           .withColumn("source", F.lit("bcb_ptax"))
    )

    sdf = sdf.select([c.name for c in BRONZE_SPARK_SCHEMA.fields])

    delta = DeltaTable.forName(spark, target_table)

    # Idempotência: evita duplicar o mesmo timestamp quando reprocessar janela
    (
        delta.alias("t")
        .merge(sdf.alias("s"), "t.dataHoraCotacao = s.dataHoraCotacao")
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )

    print(f"[BRONZE] Upsert OK -> {target_table} (rows={sdf.count()})")

# COMMAND ----------

# DBTITLE 1,Cell 12
def main() -> None:
    # spark.sql("DROP TABLE IF EXISTS bronze.br_fx_ptax_raw")
    spark.sql("SELECT current_catalog(), current_database()").show(truncate=False)
    spark.sql(f"SHOW TABLES IN {schema_fq(BRONZE_SCHEMA)}").show(truncate=False)
    target = fq(BRONZE_SCHEMA, BRONZE_TABLE)

    # Create schema/table safely (first run)
    ensure_bronze_objects(target)

    start, end = get_incremental_window(target)
    from datetime import date
    end = min(end, date.today())  # Ensure end is not in the future

    print(f"[PTAX] Fetching from {start} to {end} ...")
    rows = fetch_ptax_period(start, end)
    pdf = normalize(rows)

    print(f"[PTAX] Rows after normalize/dedup: {len(pdf)}")
    upsert_bronze(target, pdf)

    # sanity checks
    spark.sql(f"""
    SELECT
        COUNT(*) AS n,
        MIN(ds)  AS min_ds,
        MAX(ds)  AS max_ds,
        MIN(dataHoraCotacao) AS min_ts,
        MAX(dataHoraCotacao) AS max_ts
    FROM {target}
    """).show(truncate=False)


# COMMAND ----------

if __name__ == "__main__":
    main()
