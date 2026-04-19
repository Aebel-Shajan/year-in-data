"""
Aggregates job parquets into daily summary tables.
"""

from __future__ import annotations

import polars as pl

from pipeline.common import r2 as R2
from pipeline.common.config import PipelineConfig
from pipeline.common.paths import Table, table
from pipeline.common.r2 import R2Client


def aggregate_sleep(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df.group_by("date").agg(pl.col("value").sum())
        .with_columns((pl.col("value") / 60).round(2).alias("value"))
        .sort("date")
    )

def aggregate_exercise(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df.group_by("date").agg(pl.col("value").sum())
        .with_columns((pl.col("value") / 60_000).round(1).alias("value"))
        .sort("date")
    )

def aggregate_steps(df: pl.DataFrame) -> pl.DataFrame:
    return df.group_by("date").agg(pl.col("value").sum()).sort("date")


def aggregate_calories(df: pl.DataFrame) -> pl.DataFrame:
    return df.group_by("date").agg(pl.col("value").sum()).sort("date")


def aggregate_gym_group(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df.with_columns((pl.col("duration_ms") / 60_000).round(1).alias("value"))
        .select(["date", "category", "value"])
    )

def aggregate_kindle(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df.group_by(["date", "category"])
        .agg((pl.col("reading_ms").sum() / 60_000).round(1).alias("value"))
        .sort("date")
    )

def aggregate_macos_commands(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df
        .with_columns(pl.col("count")
        .cast(pl.Float64)
        .alias("value"))
        .select(["date", "category", "value"])
    )




_AGGREGATIONS = [
    ("fitbit_calories",      aggregate_calories),
    ("fitbit_steps",         aggregate_steps),
    ("fitbit_steps",      aggregate_exercise),
    ("fitbit_sleep",         aggregate_sleep),
    ("gym_group_workouts",      aggregate_gym_group),
    ("kindle_reading",       aggregate_kindle),
    ("macos_commands",       aggregate_macos_commands),
    ("macos_screentime",     aggregate_macos_scre),
    ("",      aggregate_strong_workouts),
]


def aggregate_daily(r2: R2Client, config: PipelineConfig) -> None:
    for table_name, transform in _AGGREGATIONS:
        _agg(r2, table_name, transform)


def _agg(r2: R2Client, name: str, transform) -> None:
    input_key = table(name)
    output_key = table("daily_" + name)
    df = R2.load_parquet(r2, input_key)
    if df is None:
        print(f"[{input_key}] no data, skipping")
        return
    result = transform(df)
    R2.store_parquet(r2, output_key, result, sort_col="date", overwrite=True)
    print(f"[{output_key}] {len(result)} rows")
