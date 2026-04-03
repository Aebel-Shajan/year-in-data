from __future__ import annotations
from datetime import date
import polars as pl
from pipeline import r2 as R2
from pipeline.r2 import R2Client

SOURCE = "fitbit"
METRIC = "daily_exercise"
UNIT = "minutes"
LABEL = "Active minutes"


def materialize(r2: R2Client, start: date | None = None, end: date | None = None, dry_run: bool = False) -> None:
    df = R2.load_parquet(r2, R2.silver_key("fitbit", "exercise"), start=start, end=end)
    if df is None:
        print(f"[gold/{METRIC}] no silver data, skipping")
        return

    gold = df.with_columns((pl.col("value") / 60_000).round(1).alias("value"))

    if dry_run:
        print(gold)
        return

    R2.store_parquet(r2, R2.gold_key(SOURCE, METRIC), gold, sort_col="date", overwrite=True)
    R2.export_daily_aggregated_json(r2, SOURCE, METRIC, UNIT, LABEL)
    print(f"[gold/{METRIC}] {len(gold)} rows")
