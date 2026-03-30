"""
macOS Screen Time extractor.

Reads app usage directly from the macOS knowledgeC.db SQLite database and
uploads aggregated daily totals to R2.

Requires Full Disk Access for the app running the script
(Terminal, iTerm, VSCode, etc.) — grant it in:
  System Settings → Privacy & Security → Full Disk Access

Run via scripts/sync_screentime.py on a cron schedule.
"""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import polars as pl

from pipeline import r2 as R2
from pipeline.r2 import R2Client

METRIC = "app_usage"
UNIT = "minutes"
LABEL = "Screen time"

_DB = Path.home() / "Library/Application Support/Knowledge/knowledgeC.db"

# Apple's CoreData epoch starts 2001-01-01 — offset to Unix epoch
_APPLE_EPOCH_OFFSET = 978_307_200

_QUERY = """
SELECT
    ZOBJECT.ZVALUESTRING                        AS app,
    (ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE)     AS usage_secs,
    (ZOBJECT.ZSTARTDATE + 978307200)            AS start_unix,
    ZOBJECT.ZSECONDSFROMGMT                     AS tz_offset
FROM
    ZOBJECT
    LEFT JOIN ZSOURCE ON ZOBJECT.ZSOURCE = ZSOURCE.Z_PK
WHERE
    ZSTREAMNAME = '/app/usage'
    AND ZOBJECT.ZVALUESTRING IS NOT NULL
    AND (ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE) > 0
ORDER BY
    ZOBJECT.ZSTARTDATE DESC
"""


def run(r2: R2Client) -> None:
    rows = _query_db()
    if not rows:
        print("[screentime] no data returned, skipping")
        return

    df = _to_df(rows)
    print(f"[screentime/{METRIC}] {len(df)} rows")
    R2.store_partitions(r2, "screentime", METRIC, df)
    R2.write_web_json(r2, "screentime", METRIC, UNIT, LABEL)


def _query_db(db_path: Path = _DB) -> list[tuple]:
    if not db_path.exists():
        raise FileNotFoundError(f"knowledgeC.db not found at {db_path}")
    if not os.access(db_path, os.R_OK):
        raise PermissionError(
            f"{db_path} is not readable. "
            "Grant Full Disk Access to your terminal in "
            "System Settings → Privacy & Security → Full Disk Access"
        )
    with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as con:
        return con.execute(_QUERY).fetchall()


def _to_df(rows: list[tuple]) -> pl.DataFrame:
    apps, usage_secs, start_unix, tz_offsets = zip(*rows)

    # Localise each timestamp using the per-record tz offset stored in the DB
    dates = [
        datetime.fromtimestamp(ts + (tz or 0), tz=timezone.utc).date()
        for ts, tz in zip(start_unix, tz_offsets)
    ]

    return (
        pl.DataFrame({
            "date":     list(dates),
            "value":    [round(s / 60, 1) for s in usage_secs],
            "category": list(apps),
        }, schema={"date": pl.Date, "value": pl.Float64, "category": pl.Utf8})
        .group_by(["date", "category"])
        .agg(pl.col("value").sum().round(1))
        .sort("date")
    )
