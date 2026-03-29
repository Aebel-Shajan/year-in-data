"""
Kindle extractor.

Upload your Kindle reading insights ZIP to: raw/kindle/inbox/

The ZIP contains a file named:
  Kindle.reading-insights-sessions_with_adjustments.csv

Relevant columns: start_time, product_name, total_reading_milliseconds
"""

from __future__ import annotations

import io
import zipfile

import polars as pl

from pipeline import r2 as R2
from pipeline.r2 import R2Client

METRIC = "reading"
UNIT = "minutes"
LABEL = "Reading time"

_CSV_NAME = "Kindle.reading-insights-sessions_with_adjustments.csv"
_DATE_COL = "start_time"
_DURATION_COL = "total_reading_milliseconds"
_TITLE_COL = "product_name"


def run(r2: R2Client) -> None:
    inbox = R2.inbox_prefix("kindle")
    zip_keys = [k for k in R2.list_keys(r2, inbox) if k.lower().endswith(".zip")]

    if not zip_keys:
        print("[kindle] inbox is empty, skipping")
        return

    df = pl.concat([_read_zip(R2.download_bytes(r2, k)) for k in zip_keys])

    print(f"[kindle/{METRIC}] {len(df)} rows")
    R2.store_partitions(r2, "kindle", METRIC, df)
    R2.write_web_json(r2, "kindle", METRIC, UNIT, LABEL)
    R2.archive_inbox(r2, "kindle")


def _read_zip(data: bytes) -> pl.DataFrame:
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        matches = [n for n in zf.namelist() if n.endswith(_CSV_NAME)]
        if not matches:
            raise FileNotFoundError(f"{_CSV_NAME} not found in ZIP")
        csv_data = zf.read(matches[0])
    return _read_csv(csv_data)


def _read_csv(data: bytes) -> pl.DataFrame:
    df = pl.read_csv(io.BytesIO(data), infer_schema_length=1000)

    df = df.filter(pl.col(_DURATION_COL).is_not_null())

    df = df.with_columns(
        pl.col(_DATE_COL).str.slice(0, 10).str.to_date("%Y-%m-%d").alias("date"),
        (pl.col(_DURATION_COL).cast(pl.Float64) / 60_000).round(1).alias("value"),
        pl.col(_TITLE_COL).fill_null("Unknown").alias("category"),
    )

    # Daily totals per book title
    return (
        df.select(["date", "value", "category"])
        .group_by(["date", "category"])
        .agg(pl.col("value").sum())
        .sort("date")
    )
