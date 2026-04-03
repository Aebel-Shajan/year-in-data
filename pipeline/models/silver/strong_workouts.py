"""
Silver table: strong/workouts

Reads Strong app CSV exports from the bronze inbox. Strong records one row
per exercise set and repeats the full session duration on every row, so
silver collapses to one row per (date, workout) using max(duration_sec).

Silver schema: (date, category, duration_sec)
"""

from __future__ import annotations

import io
from datetime import date

import polars as pl

from pipeline import r2 as R2
from pipeline.r2 import R2Client

SOURCE = "strong"
METRIC = "workouts"


def materialize(r2: R2Client, start: date | None = None, end: date | None = None) -> None:
    keys = [k for k in R2.list_archived_keys(r2, SOURCE, start=start, end=end) if k.lower().endswith(".csv")]
    if not keys:
        print(f"[silver/{SOURCE}/{METRIC}] no archived files found, skipping")
        return

    frames = [_parse_csv(R2.download_bytes(r2, k)) for k in keys]
    df = (
        pl.concat(frames)
        .group_by(["date", "category"])
        .agg(pl.col("duration_sec").max())
        .sort("date")
    )

    R2.store_parquet(r2, R2.silver_key(SOURCE, METRIC), df, sort_col="date", overwrite=True)
    print(f"[silver/{SOURCE}/{METRIC}] {len(df)} rows")


def _parse_csv(data: bytes) -> pl.DataFrame:
    return (
        pl.read_csv(io.BytesIO(data), separator=";", infer_schema_length=1000)
        .with_columns(
            pl.col("Date").str.slice(0, 10).str.to_date("%Y-%m-%d").alias("date"),
            pl.col("Workout Name").alias("category"),
            pl.col("Duration (sec)").cast(pl.Float64).alias("duration_sec"),
        )
        .select(["date", "category", "duration_sec"])
    )
