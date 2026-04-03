"""
Silver table: screentime/app_usage

Reads archived bronze JSON files and produces a silver table with daily
usage per app in source units (seconds).

Silver schema: (date, category, usage_secs)
"""

from __future__ import annotations

import json
from datetime import date, datetime, timezone

import polars as pl

from pipeline import r2 as R2
from pipeline.r2 import R2Client

SOURCE = "screentime"
METRIC = "app_usage"


def materialize(r2: R2Client, start: date | None = None, end: date | None = None) -> None:
    keys = [k for k in R2.list_archived_keys(r2, SOURCE, start=start, end=end) if k.endswith(".json")]
    if not keys:
        print(f"[silver/{SOURCE}/{METRIC}] no archived files found, skipping")
        return

    all_records: list[dict] = []
    for key in keys:
        all_records.extend(json.loads(R2.download_bytes(r2, key)))

    dates = [
        datetime.fromtimestamp(r["start_unix"] + r["tz_offset"], tz=timezone.utc).date()
        for r in all_records
    ]
    df = (
        pl.DataFrame(
            {
                "date": dates,
                "category": [r["app"] for r in all_records],
                "usage_secs": [r["usage_secs"] for r in all_records],
            },
            schema={"date": pl.Date, "category": pl.Utf8, "usage_secs": pl.Float64},
        )
        .group_by(["date", "category"])
        .agg(pl.col("usage_secs").sum())
        .sort("date")
    )

    R2.store_parquet(r2, R2.silver_key(SOURCE, METRIC), df, sort_col="date", overwrite=True)
    print(f"[silver/{SOURCE}/{METRIC}] {len(df)} rows")
