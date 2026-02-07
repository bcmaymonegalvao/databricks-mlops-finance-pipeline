# Databricks notebook source
# MAGIC %md
# MAGIC # 01 — Ingest → Bronze (placeholder)
# MAGIC

# COMMAND ----------

from __future__ import annotations

import os
from datetime import date, datetime, timedelta
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

# COMMAND ----------

# DBTITLE 1,Fix SyntaxError in bcb_date function
def fq(schema: str, table: str):
    """Fully-qualifyed table name, with optional Unity Catalog"""
    return f"{CATALOG}.{schema}.{table}" if CATALOG else f"{schema}.table"


def schema_fq(schema: str) -> str:
    return f"{CATALOG}.{schema}" if CATALOG else schema


def bcb_date(d: date) -> str:
    """BCB OData expects 'MM-DD-YYYY' wrapped in single quotes."""
    return f"'{d.strftime('%m-%d-%Y')}'"


def table_exists(name: str) -> bool:
    try:
        spark.table(name) # type: ignore[name-defined]
        return True
    except Exception:
        return False

# COMMAND ----------

# DBTITLE 1,Fix SyntaxError in get_incremental_window
def get_incremental_window(target_table: str) -> tuple[date, date]:
    """
    Estratégia incremental:
    - Se a table existe: Volta 7 dias (buffer) a partir do max(ds)
    - senão: usa DEFAULT_LOOKBACK_DAYS
    """
    end = date.today()
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
    return start, end

# COMMAND ----------

def fetch_ptax_period(start: date, end: date, top: int = 10000) -> list[dict[str, Any]]:
    """
    Busca PTAX (USD) por período via OData.
    Filtra tipoBoletim='Fechamento' e página com $skip/$top.
    """
    endpoint = f"{PTAX_BASE}/{PTAX_RESOURCE}(data_inicial=@dataInicial, dataFinalCotacao=@dataFinalCotacao)"

    all_rows: list[dict[str, Any]] = []
    skip = 0

    while True:
        params = {
            "@dataInicial": bcb_date(start),
            "@dataFinalCotacao": bcb_date(end),
            "$format": "json",
            "$select": "cotacaoCompra, cotacaoVenda, dataHoraCotacao, tipoBoletim",
            "$filter": "tipoBoletim eq 'Fechamento'",
            "$top": str(top),
            "$skip": str(skip)
        }

        r = requests.get(endpoint, params=params, timeout=60)
        r.raise_for_status()
        payload = r.json()
        rows = payload.get("value", [])
        if not rows:
            break

        all_rows.extend(rows)

        if len(rows) < top:
            break
        skip += top

    return all_rows

# COMMAND ----------

def normalize(rows: list[dict[str, Any]]) -> pd.DataFrame:
    """
    Normaliza para o schema Bronze (raw-but-usable).
    Mantém 1 linha por dia (ds), pegando o último dataHoraCotacao do dia
    """
    if not rows:
        return pd.DataFrame(columns=["ds", "ptax_buy", "ptax_sell", "tipoBoletim", "source"])
    
    pdf = pd.DataFrame(rows).copy()
    pdf["dataHoraCotacao"] = pd.to_datetime(pdf["dataHoraCotacao"], errors="coerce")
    pdf["ds"] = pdf["dataHoraCotacao"].dt.date

    pdf = pdf.rename(
        columns={
            "cotacaoCompra": "ptax_buy",
            "cotacaoVenda": "ptax_sell",
        }
    )

    # garantir numérico
    pdf["ptax_buy"] = pd.to_numeric(pdf["ptax_buy"], errors="coerce")
    pdf["ptax_sell"] = pd.to_numeric(pdf["ptax_sell"], errors="coerce")

    # 1 registro por ds (último do dia)
    pdf = pdf.sort_values("dataHoraCotacao").drop_duplicates(subset=["ds"], keep="last")

    pdf["source"] = "bcb_ptax"
    return pdf[["ds", "ptax_buy", "ptax_sell", "dataHoraCotacao", "tipoBoletim", "source"]]


# COMMAND ----------

def upsert_bronze(target_table: str, pdf: pd.DataFrame) -> None:
    if pdf.empty:
        print("Nenhum dado retornado pela API para o período informado.")
        return
    
    sdf = spark.createDataFrame(pdf) # type: ignore[name-defined]

    # tipagem consistente
    sdf = (
        sdf.withColumn("ds", F.to_date("ds"))
        .withColumn("ptax_buy", F.col("ptax_buy").cast("double"))
        .withColumn("ptax_sell", F.col(ptax_sell).cast("double"))
        .withColumn("dataHoraCotacao", F.to_timestamp("dataHoraCotacao"))
        .withColumn("ingestion_ts", F.current_timestamp())
    )

    # garante schema/database
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {schema_fq(BRONZE_SCHEMA)}") # type: ignore[name-defined]

    if not table_exists(target_table):
        (
            sdf.write.format("delta")
            .mode("overwrite")
            .savaAsTable(target_table)
        )
        print(f"Tabela")

    # merge idempotente por ds
    delta = DeltaTable.forName(spark, target_table) # ta
