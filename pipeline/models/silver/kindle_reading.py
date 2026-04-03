"""
Silver table: kindle/reading

Reads archived Kindle ZIP files and produces a silver table with daily
reading time per book in source units (milliseconds).

Silver schema: (date, category, reading_ms)
"""

from __future__ import annotations

import io
import zipfile
from datetime import date

import polars as pl

from pipeline import r2 as R2
from pipeline.r2 import R2Client

SOURCE = "kindle"
METRIC = "reading"

_CSV_NAME = "Kindle.reading-insights-sessions_with_adjustments.csv"


def materialize(r2: R2Client, start: date | None = None, end: date | None = None) -> None:
    keys = [k for k in R2.list_archived_keys(r2, SOURCE, start=start, end=end) if k.lower().endswith(".zip")]
    if not keys:
        print(f"[silver/{SOURCE}/{METRIC}] no archived files found, skipping")
        return

    frames = [_parse_zip(R2.download_bytes(r2, k)) for k in keys]
    df = (
        pl.concat(frames)
        .group_by(["date", "category"])
        .agg(pl.col("reading_ms").sum())
        .sort("date")
    )

    R2.store_parquet(r2, R2.silver_key(SOURCE, METRIC), df, sort_col="date", overwrite=True)
    print(f"[silver/{SOURCE}/{METRIC}] {len(df)} rows")


def _parse_zip(data: bytes) -> pl.DataFrame:
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        matches = [n for n in zf.namelist() if n.endswith(_CSV_NAME)]
        if not matches:
            raise FileNotFoundError(f"{_CSV_NAME} not found in ZIP")
        csv_bytes = zf.read(matches[0])

    raw = pl.read_csv(io.BytesIO(csv_bytes), infer_schema_length=1000)
    return (
        raw
        .filter(pl.col("total_reading_milliseconds").is_not_null())
        .with_columns(
            pl.col("start_time").str.slice(0, 10).str.to_date("%Y-%m-%d").alias("date"),
            pl.col("product_name").fill_null("Unknown").alias("category"),
            pl.col("total_reading_milliseconds").cast(pl.Float64).alias("reading_ms"),
        )
        .select(["date", "category", "reading_ms"])
    )
