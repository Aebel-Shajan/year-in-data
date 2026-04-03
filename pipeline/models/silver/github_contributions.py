"""
Silver table: github/contributions

Reads archived bronze JSON files. The GitHub GraphQL API already returns
daily counts, so silver is a direct parse with deduplication (latest wins).

Silver schema: (date, value)  — value = contribution count
"""

from __future__ import annotations

import json
from datetime import date

import polars as pl

from pipeline import r2 as R2
from pipeline.r2 import R2Client

SOURCE = "github"
METRIC = "contributions"


def materialize(r2: R2Client, start: date | None = None, end: date | None = None) -> None:
    keys = sorted(k for k in R2.list_archived_keys(r2, SOURCE, start=start, end=end) if k.endswith(".json"))
    if not keys:
        print(f"[silver/{SOURCE}/{METRIC}] no archived files found, skipping")
        return

    all_days: list[dict] = []
    for key in keys:
        all_days.extend(json.loads(R2.download_bytes(r2, key)))

    df = (
        pl.DataFrame(
            {
                "date": [date.fromisoformat(d["date"]) for d in all_days],
                "value": [float(d["contributionCount"]) for d in all_days],
            },
            schema={"date": pl.Date, "value": pl.Float64},
        )
        .sort("date")
        .unique(subset=["date"], keep="last")
        .sort("date")
    )

    R2.store_parquet(r2, R2.silver_key(SOURCE, METRIC), df, sort_col="date", overwrite=True)
    print(f"[silver/{SOURCE}/{METRIC}] {len(df)} rows")
