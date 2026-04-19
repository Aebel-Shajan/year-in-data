"""
Source: kindle

Processes Kindle Google Takeout ZIPs uploaded manually to the inbox.
"""

from __future__ import annotations

import io
import zipfile
from datetime import date

import polars as pl

from pipeline.common import r2 as R2
from pipeline.common.config import PipelineConfig
from pipeline.common import paths
from pipeline.common.paths import Source, Table
from pipeline.common.r2 import R2Client

TAG = Source.KINDLE

_CSV_NAME = "Kindle.reading-insights-sessions_with_adjustments.csv"

def extract_kindle(r2: R2Client, config: PipelineConfig) -> None:
    R2.flush_inbox(r2, TAG, paths.inbox(TAG), paths.archive(TAG))

    archive_keys = R2.get_archive_keys(r2, paths.archive(TAG), paths.table(Table.KINDLE_READING), ".zip")
    if not archive_keys:
        print(f"[{TAG}] no new files, skipping")
        return

    frames = [_parse_zip(R2.download_bytes(r2, k)) for k in archive_keys]
    df = (
        pl.concat(frames)
        .group_by(["date", "category"])
        .agg(pl.col("reading_ms").sum())
        .sort("date")
    )

    R2.store_parquet(r2, paths.table(Table.KINDLE_READING), df, sort_col="date", overwrite=True)
    print(f"[{TAG}] {len(df)} rows")


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
