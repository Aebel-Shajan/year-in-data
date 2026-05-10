"""
Aggregates job parquets into daily summary tables.
"""

from __future__ import annotations

from typing import Callable

import polars as pl

from pipeline.common import r2 as R2
from pipeline.common.config import PipelineConfig
from pipeline.common.paths import Table, construct_table_path
from pipeline.common.r2 import R2Client


def _aggregate_steps(fitbit_df: pl.DataFrame | None, garmin_df: pl.DataFrame | None) -> pl.DataFrame:
    parts = []
    if fitbit_df is not None:
        parts.append(fitbit_df.group_by("date").agg(pl.col("value").sum()))
    if garmin_df is not None:
        parts.append(garmin_df.select(pl.col("date"), pl.col("steps").alias("value")).drop_nulls("value"))
    return pl.concat(parts).group_by("date").agg(pl.col("value").max()).sort("date")

def _aggregate_calories(fitbit_df: pl.DataFrame | None, garmin_df: pl.DataFrame | None) -> pl.DataFrame:
    parts = []
    if fitbit_df is not None:
        parts.append(fitbit_df.group_by("date").agg(pl.col("value").sum()))
    if garmin_df is not None:
        parts.append(garmin_df.select(pl.col("date"), pl.col("calories").alias("value")).drop_nulls("value"))
    return pl.concat(parts).group_by("date").agg(pl.col("value").max()).sort("date")

def _aggregate_sleep(fitbit_df: pl.DataFrame | None, garmin_df: pl.DataFrame | None) -> pl.DataFrame:
    parts = []
    if fitbit_df is not None:
        parts.append(
            fitbit_df.group_by("date").agg(pl.col("value").sum())
            .with_columns((pl.col("value") / 60).round(2).alias("value"))
        )
    if garmin_df is not None:
        parts.append(
            garmin_df.select(pl.col("date"), (pl.col("sleep_seconds") / 3600).round(2).alias("value"))
            .drop_nulls("value")
        )
    return pl.concat(parts).group_by("date").agg(pl.col("value").max()).sort("date")

def _aggregate_exercise(fitbit_df: pl.DataFrame | None, garmin_df: pl.DataFrame | None) -> pl.DataFrame:
    if fitbit_df is None:
        return pl.DataFrame({"date": [], "value": []}, schema={"date": pl.Date, "value": pl.Float64})
    return (
        fitbit_df.group_by("date").agg(pl.col("value").sum())
        .with_columns((pl.col("value") / 60_000).round(1).alias("value"))
        .sort("date")
    )

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
        df.with_columns(pl.col("count").cast(pl.Float64).alias("value"))
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


_AGGREGATIONS: list[tuple[list[Table], Table, Callable]] = [
    ([Table.FITBIT_CALORIES, Table.GARMIN_WELLNESS],      Table.DAILY_CALORIES,      _aggregate_calories),
    ([Table.FITBIT_STEPS, Table.GARMIN_WELLNESS],         Table.DAILY_STEPS,          _aggregate_steps),
    ([Table.FITBIT_EXERCISE, Table.GARMIN_WELLNESS],      Table.DAILY_EXERCISE,       _aggregate_exercise),
    ([Table.FITBIT_SLEEP, Table.GARMIN_WELLNESS],         Table.DAILY_SLEEP,          _aggregate_sleep),
    ([Table.GITHUB_CONTRIBUTIONS], Table.DAILY_GITHUB_CONTRIBUTIONS,  lambda df: df),
    ([Table.GYMGROUP_VISITS],      Table.DAILY_GYMGROUP_VISITS,       _aggregate_gym_group),
    ([Table.KINDLE_READING],       Table.DAILY_KINDLE_READING,        _aggregate_kindle),
    ([Table.MACOS_COMMANDS],       Table.DAILY_MACOS_COMMANDS,        _aggregate_macos_commands),
    ([Table.MACOS_SCREENTIME],     Table.DAILY_MACOS_SCREENTIME,      _aggregate_macos_screentime),
    ([Table.STRONG_WORKOUTS],      Table.DAILY_STRONG_WORKOUTS,       _aggregate_strong_workouts),
]


def aggregate_into_daily_tables(r2: R2Client, config: PipelineConfig) -> None:
    for inputs, output, transform in _AGGREGATIONS:
        _agg(r2, inputs=inputs, output=output, transform=transform)


def _agg(r2: R2Client, inputs: list[Table], output: Table, transform: Callable) -> None:
    frames = [R2.load_parquet(r2, construct_table_path(t)) for t in inputs]
    if all(df is None for df in frames):
        print(f"[{output}] no data, skipping")
        return

    result = transform(*frames)
    R2.store_parquet(r2, construct_table_path(output), result, sort_col="date", overwrite=True)
    print(f"[{output}] {len(result)} rows")
