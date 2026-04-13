"""
Aggregates job parquets into daily summary tables.

Reads raw job outputs and writes to daily/, applying unit conversions.
"""

from __future__ import annotations

import polars as pl

from pipeline import r2 as R2
from pipeline.config import PipelineConfig
from pipeline.paths import table
from pipeline.r2 import R2Client



def run_job(r2: R2Client, config: PipelineConfig, dry_run: bool = False) -> None:
    for name, transform in _AGGREGATIONS:
        _agg(r2, name, transform, dry_run)


# ── Transforms ────────────────────────────────────────────────────────────────

def _fitbit_daily(df: pl.DataFrame) -> pl.DataFrame:
    return df.group_by("date").agg(pl.col("value").sum()).sort("date")

def _fitbit_exercise(df: pl.DataFrame) -> pl.DataFrame:
    return _fitbit_daily(df).with_columns((pl.col("value") / 60_000).round(1).alias("value"))

def _fitbit_sleep(df: pl.DataFrame) -> pl.DataFrame:
    return _fitbit_daily(df).with_columns((pl.col("value") / 60).round(2).alias("value"))

def _gymgroup_visits(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df.with_columns((pl.col("duration_ms") / 60_000).round(1).alias("value"))
        .select(["date", "category", "value"])
    )

def _kindle_reading(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df.group_by(["date", "category"])
        .agg((pl.col("reading_ms").sum() / 60_000).round(1).alias("value"))
        .sort("date")
    )

def _macos_commands(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(pl.col("count").cast(pl.Float64).alias("value")).select(["date", "category", "value"])

def _macos_screentime(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df.group_by(["date", "category"])
        .agg((pl.col("usage_secs").sum() / 60).round(1).alias("value"))
        .sort("date")
    )

def _strong_workouts(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df.with_columns((pl.col("duration_sec") / 60).round(1).alias("value"))
        .select(["date", "category", "value"])
    )


_AGGREGATIONS = [
    ("fitbit_calories", _fitbit_daily),
    ("fitbit_steps",   _fitbit_daily),
    ("fitbit_exercise",      _fitbit_exercise),
    ("fitbit_sleep",         _fitbit_sleep),
    ("github_contributions", None),
    ("gymgroup_visits",    _gymgroup_visits),
    ("kindle_reading",       _kindle_reading),
    ("macos_commands",      _macos_commands),
    ("macos_screentime",  _macos_screentime),
    ("strong_workouts",      _strong_workouts),
]


# ── Internal ──────────────────────────────────────────────────────────────────

def _agg(r2: R2Client, name: str, transform, dry_run: bool) -> None:
    input_key = table(name)
    output_key = table("daily_"+name)
    df = R2.load_parquet(r2, input_key)
    if df is None:
        print(f"[{input_key}] no data, skipping")
        return
    result = transform(df) if transform else df
    if dry_run:
        print(result)
        return
    R2.store_parquet(r2, output_key, result, sort_col="date", overwrite=True)
    print(f"[{output_key}] {len(result)} rows")
