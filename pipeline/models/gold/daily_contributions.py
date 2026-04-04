from __future__ import annotations
from datetime import date
from pipeline import r2 as R2
from pipeline.r2 import R2Client


def daily_contributions(r2: R2Client, input_key: str, output_key: str, unit: str, label: str, start: date | None = None, end: date | None = None, dry_run: bool = False) -> None:
    start = start or R2.latest_date(r2, output_key)
    gold = R2.load_parquet(r2, input_key, start=start, end=end)
    if gold is None:
        print(f"[{output_key.removesuffix('.parquet')}] no silver data, skipping")
        return

    if dry_run:
        print(gold)
        return

    R2.store_parquet(r2, output_key, gold, sort_col="date", overwrite=True)
    R2.export_daily_aggregated_json(r2, output_key, unit, label)
    print(f"[{output_key.removesuffix('.parquet')}] {len(gold)} rows")
