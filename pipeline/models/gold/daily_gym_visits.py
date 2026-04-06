from __future__ import annotations
from datetime import date
import polars as pl
from pipeline import r2 as R2
from pipeline.r2 import R2Client


def daily_gym_visits(r2: R2Client, input_key: str, output_key: str, unit: str, label: str, start: date | None = None, end: date | None = None, dry_run: bool = False) -> None:
    # start = start or R2.latest_date(r2, output_key)
    df = R2.load_parquet(r2, input_key, start=start, end=end)
    if df is None:
        print(f"[{output_key.removesuffix('.parquet')}] no silver data, skipping")
        return

    print(start, end)
    gold = (
        df.with_columns((pl.col("duration_ms") / 60_000).round(1).alias("value"))
    )




    R2.store_parquet(r2, output_key, gold, sort_col="date", overwrite=True)
    print(f"[{output_key.removesuffix('.parquet')}] {len(gold)} rows")
