"""
Silver table: gymgroup/visits

Reads archived bronze JSON files and produces a silver table with daily
duration per gym location in source units (milliseconds).

Silver schema: (date, category, duration_ms)
"""

from __future__ import annotations

import json
from datetime import date

import polars as pl

from pipeline import r2 as R2
from pipeline.r2 import R2Client

SOURCE = "gymgroup"
METRIC = "visits"


def materialize(r2: R2Client, start: date | None = None, end: date | None = None) -> None:
    keys = [k for k in R2.list_archived_keys(r2, SOURCE, start=start, end=end) if k.endswith(".json")]
    if not keys:
        print(f"[silver/{SOURCE}/{METRIC}] no archived files found, skipping")
        return

    all_check_ins: list[dict] = []
    for key in keys:
        all_check_ins.extend(json.loads(R2.download_bytes(r2, key)))

    df = (
        pl.DataFrame(all_check_ins)
        .select(["checkInDate", "gymLocationName", "duration"])
        .filter(pl.col("duration") > 0)
        .with_columns(
            pl.col("checkInDate").str.slice(0, 10).str.to_date("%Y-%m-%d").alias("date"),
            pl.col("gymLocationName").alias("category"),
            pl.col("duration").cast(pl.Float64).alias("duration_ms"),
        )
        .select(["date", "category", "duration_ms"])
        .group_by(["date", "category"])
        .agg(pl.col("duration_ms").sum())
        .sort("date")
    )

    R2.store_parquet(r2, R2.silver_key(SOURCE, METRIC), df, sort_col="date", overwrite=True)
    print(f"[silver/{SOURCE}/{METRIC}] {len(df)} rows")
