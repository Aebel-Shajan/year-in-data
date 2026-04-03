"""
Silver table: zsh_history/commands

Reads raw command JSON from the bronze inbox and produces a silver table
with daily counts per command stem.

Silver schema: (date, category, count)
"""

from __future__ import annotations

import json
from datetime import date

import polars as pl

from pipeline import r2 as R2
from pipeline.r2 import R2Client

SOURCE = "zsh_history"
METRIC = "commands"


def materialize(r2: R2Client, start: date | None = None, end: date | None = None) -> None:
    keys = [k for k in R2.list_archived_keys(r2, SOURCE, start=start, end=end) if k.endswith(".json")]
    if not keys:
        print(f"[silver/{SOURCE}/{METRIC}] no archived files found, skipping")
        return

    all_records: list[dict] = []
    for key in keys:
        all_records.extend(json.loads(R2.download_bytes(r2, key)))

    df = (
        pl.DataFrame(
            {
                "date": [date.fromisoformat(r["date"]) for r in all_records],
                "category": [r["command"] for r in all_records],
            },
            schema={"date": pl.Date, "category": pl.Utf8},
        )
        .with_columns(pl.lit(1).cast(pl.Int64).alias("count"))
        .group_by(["date", "category"])
        .agg(pl.col("count").sum())
        .sort("date")
    )

    R2.store_parquet(r2, R2.silver_key(SOURCE, METRIC), df, sort_col="date", overwrite=True)
    print(f"[silver/{SOURCE}/{METRIC}] {len(df)} rows")
