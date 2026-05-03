"""
Aggregates job parquets into daily summary tables.
"""

from __future__ import annotations

import polars as pl

from pipeline.common import r2 as R2
from pipeline.common.config import PipelineConfig
from pipeline.common.paths import Table, construct_table_path
from pipeline.common.r2 import R2Client


def _aggregate_sleep(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df.group_by("date").agg(pl.col("value").sum())
        .with_columns((pl.col("value") / 60).round(2).alias("value"))
        .sort("date")
    )

def _aggregate_exercise(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df.group_by("date").agg(pl.col("value").sum())
        .with_columns((pl.col("value") / 60_000).round(1).alias("value"))
        .sort("date")
    )

def _aggregate_steps(df: pl.DataFrame) -> pl.DataFrame:
    return df.group_by("date").agg(pl.col("value").sum()).sort("date")


def _aggregate_calories(df: pl.DataFrame) -> pl.DataFrame:
    return df.group_by("date").agg(pl.col("value").sum()).sort("date")


def _aggregate_gym_group(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df.with_columns((pl.col("duration_ms") / 60_000).round(1).alias("value"))
        .select(["date", "category", "value"])
    )

def _aggregate_kindle(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df.group_by(["date", "category"])
        .agg((pl.col("reading_ms").sum() / 60_000).round(1).alias("value"))
        .sort("date")
    )

def _aggregate_macos_commands(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df
        .with_columns(pl.col("count")
        .cast(pl.Float64)
        .alias("value"))
        .select(["date", "category", "value"])
    )

def _aggregate_macos_screentime(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df.group_by(["date", "category"])
        .agg((pl.col("usage_secs").sum() / 60).round(1).alias("value"))
        .sort("date")
    )

def _aggregate_strong_workouts(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df.with_columns((pl.col("duration_sec") / 60).round(1).alias("value"))
        .select(["date", "category", "value"])
    )




_AGGREGATIONS = [
    ("fitbit_calories",       _aggregate_calories),
    ("fitbit_steps",          _aggregate_steps),
    ("fitbit_exercise",       _aggregate_exercise),
    ("fitbit_sleep",          _aggregate_sleep),
    ("github_contributions",  lambda df: df),
    ("gymgroup_visits",       _aggregate_gym_group),
    ("kindle_reading",        _aggregate_kindle),
    ("macos_commands",        _aggregate_macos_commands),
    ("macos_screentime",      _aggregate_macos_screentime),
    ("strong_workouts",       _aggregate_strong_workouts),
]


def aggregate_into_daily_tables(r2: R2Client, config: PipelineConfig) -> None:
    for table_name, transform in _AGGREGATIONS:
        _agg(r2, table_name, transform)


def _agg(r2: R2Client, name: str, transform) -> None:
    input_key = construct_table_path(name)
    output_key = construct_table_path("daily_" + name)
    df = R2.load_parquet(r2, input_key)
    if df is None:
        print(f"[{input_key}] no data, skipping")
        return
    result = transform(df)
    R2.store_parquet(r2, output_key, result, sort_col="date", overwrite=True)
    print(f"[{output_key}] {len(result)} rows")
