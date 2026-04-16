"""
Source: macos_screentime

Processes inbox files containing macOS app usage sessions.
Fetch data first with: uv run python scripts/sync_macos.py

Requires Full Disk Access for the terminal running sync_macos.py:
  System Settings → Privacy & Security → Full Disk Access
"""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import date, datetime, timezone
from pathlib import Path

import polars as pl

from pipeline import paths, r2 as R2
from pipeline.config import PipelineConfig
from pipeline.paths import Source, Table
from pipeline.r2 import R2Client

TAG = Source.MACOS_SCREENTIME

_DB = Path.home() / "Library/Application Support/Knowledge/knowledgeC.db"

_QUERY = """
SELECT
    ZOBJECT.ZVALUESTRING                        AS app,
    (ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE)     AS usage_secs,
    (ZOBJECT.ZSTARTDATE + 978307200)            AS start_unix,
    ZOBJECT.ZSECONDSFROMGMT                     AS tz_offset
FROM
    ZOBJECT
WHERE
    ZSTREAMNAME = '/app/usage'
    AND ZOBJECT.ZVALUESTRING IS NOT NULL
    AND (ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE) > 0
ORDER BY
    ZOBJECT.ZSTARTDATE DESC
"""

def fetch(r2: R2Client, config: PipelineConfig) -> None:
    """Query knowledgeC.db and upload to inbox."""
    records = _query_db()
    filename = f"screentime_{date.today().isoformat()}.json"
    R2.upload_bytes(r2, paths.inbox(TAG) + "/" + filename, json.dumps(records).encode(), "application/json")
    print(f"[{TAG}] {len(records)} screentime records → inbox")


def process_macos_screentime(r2: R2Client, config: PipelineConfig) -> None:
    R2.flush_inbox(r2, TAG, paths.inbox(TAG), paths.archive(TAG))

    archive_keys = R2.get_archive_keys(r2, paths.archive(TAG), paths.table(Table.MACOS_SCREENTIME), ".json")
    if not archive_keys:
        print(f"[{TAG}] no new files, skipping")
        return

    all_records: list[dict] = []
    for key in archive_keys:
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

    R2.store_parquet(r2, paths.table(Table.MACOS_SCREENTIME), df, sort_col="date", overwrite=True)
    print(f"[{TAG}] {len(df)} rows")


# ── Aggregation ───────────────────────────────────────────────────────────────

def aggregate(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df.group_by(["date", "category"])
        .agg((pl.col("usage_secs").sum() / 60).round(1).alias("value"))
        .sort("date")
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _query_db(db_path: Path = _DB) -> list[dict]:
    if not db_path.exists():
        raise FileNotFoundError(f"knowledgeC.db not found at {db_path}")
    if not os.access(db_path, os.R_OK):
        raise PermissionError(
            f"{db_path} is not readable. "
            "Grant Full Disk Access to your terminal in "
            "System Settings → Privacy & Security → Full Disk Access"
        )
    with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as con:
        rows = con.execute(_QUERY).fetchall()
        return [
            {"app": app, "usage_secs": secs, "start_unix": unix, "tz_offset": tz or 0}
            for app, secs, unix, tz in rows
        ]
