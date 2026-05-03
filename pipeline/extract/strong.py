"""
Source: strong

Processes Strong app CSV exports uploaded manually to the inbox.
"""

from __future__ import annotations

import io

import polars as pl

from pipeline.common import r2 as R2
from pipeline.common.config import PipelineConfig
from pipeline.common import paths
from pipeline.common.paths import Source, Table
from pipeline.common.r2 import R2Client

TAG = Source.STRONG


def extract_strong(r2: R2Client, config: PipelineConfig) -> None:
    R2.flush_inbox(r2, TAG, paths.construct_inbox_path(TAG), paths.construct_archive_path(TAG))

    archive_keys = R2.get_archive_keys(r2, paths.construct_archive_path(TAG), paths.construct_table_path(Table.STRONG_WORKOUTS), ".csv")
    if not archive_keys:
        print(f"[{TAG}] no new files, skipping")
        return

    frames = [_parse_csv(R2.download_bytes(r2, k)) for k in archive_keys]
    df = (
        pl.concat(frames)
        .group_by(["date", "category"])
        .agg(pl.col("duration_sec").max())
        .sort("date")
    )

    R2.store_parquet(r2, paths.construct_table_path(Table.STRONG_WORKOUTS), df, sort_col="date", dedup_cols=["date", "category"], overwrite=True)
    print(f"[{TAG}] {len(df)} rows")


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
