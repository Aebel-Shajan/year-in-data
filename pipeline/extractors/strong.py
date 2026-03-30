"""
Strong app extractor.

Export a CSV from the Strong app and upload to: raw/strong/inbox/

Strong's CSV export has columns:
  Date, Workout Name, Duration (sec), Exercise Name, Set Order, Weight (kg),
  Reps, RPE, Distance (meters), Seconds, Notes, Workout Notes
"""

from __future__ import annotations

import io

import polars as pl

from pipeline import r2 as R2
from pipeline.r2 import R2Client

METRIC = "workouts"
UNIT = "minutes"
LABEL = "Workout duration"

_DATE_COL = "Date"
_WORKOUT_COL = "Workout Name"
_DURATION_COL = "Duration (sec)"


def run(r2: R2Client) -> None:
    inbox = R2.inbox_prefix("strong")
    csv_keys = [k for k in R2.list_keys(r2, inbox) if k.lower().endswith(".csv")]

    if not csv_keys:
        print("[strong] inbox is empty, skipping")
        return

    df = (
        pl.concat([_read_csv(R2.download_bytes(r2, k)) for k in csv_keys])
        .group_by(["date", "category"])
        .agg(pl.col("value").max())
        .sort("date")
    )

    print(f"[strong/{METRIC}] {len(df)} rows")
    R2.store_partitions(r2, "strong", METRIC, df)
    R2.write_web_json(r2, "strong", METRIC, UNIT, LABEL)
    R2.archive_inbox(r2, "strong")


def _read_csv(data: bytes) -> pl.DataFrame:
    df = pl.read_csv(io.BytesIO(data), separator=";", infer_schema_length=1000)

    # One row per set — collapse to one row per workout session
    df = df.with_columns(
        pl.col(_DATE_COL).str.slice(0, 10).str.to_date("%Y-%m-%d").alias("date"),
        pl.col(_WORKOUT_COL).alias("category"),
        (pl.col(_DURATION_COL).cast(pl.Float64) / 60).round(1).alias("value"),
    )

    # One row per (date, workout name): keep max duration (the full session duration)
    return (
        df.select(["date", "value", "category"])
        .group_by(["date", "category"])
        .agg(pl.col("value").max())
        .sort("date")
    )
