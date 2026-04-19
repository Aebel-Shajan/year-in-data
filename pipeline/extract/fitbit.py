"""
Source: fitbit

Processes Fitbit Google Takeout ZIPs uploaded manually to the inbox.
Produces four metrics: calories, exercise, sleep, steps.
"""

from __future__ import annotations

import io
import json
import re
import zipfile
from datetime import datetime

import polars as pl

from pipeline.common import r2 as R2
from pipeline.common.config import PipelineConfig
from pipeline.common import paths
from pipeline.common.paths import Source, Table
from pipeline.common.r2 import R2Client

TAG = Source.FITBIT

_CALORIES_RE = re.compile(r"Fitbit/Global Export Data/calories-\d{4}-\d{2}-\d{2}\.json$", re.IGNORECASE)
_EXERCISE_RE = re.compile(r"Fitbit/Global Export Data/exercise-\d{4}-\d{2}-\d{2}\.json$", re.IGNORECASE)
_SLEEP_RE    = re.compile(r"Fitbit/Global Export Data/sleep-\d{4}-\d{2}-\d{2}\.json$",    re.IGNORECASE)
_STEPS_RE    = re.compile(r"Fitbit/Global Export Data/steps-\d{4}-\d{2}-\d{2}\.json$",    re.IGNORECASE)


def extract_fitbit(r2: R2Client, config: PipelineConfig) -> None:
    R2.flush_inbox(r2, TAG, paths.construct_inbox_path(TAG), paths.construct_archive_path(TAG))

    _parse_metric(r2, paths.construct_table_path(Table.FITBIT_CALORIES), _CALORIES_RE, "dateTime",    "value")
    _parse_metric(r2, paths.construct_table_path(Table.FITBIT_EXERCISE), _EXERCISE_RE, "startTime",   "activeDuration")
    _parse_metric(r2, paths.construct_table_path(Table.FITBIT_SLEEP),    _SLEEP_RE,    "dateOfSleep", "minutesAsleep")
    _parse_metric(r2, paths.construct_table_path(Table.FITBIT_STEPS),    _STEPS_RE,    "dateTime",    "value")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_metric(
    r2: R2Client,
    output_key: str,
    file_re: re.Pattern,
    date_field: str,
    value_field: str,
) -> None:
    label = output_key.split("/")[-1].removesuffix(".parquet")
    keys = R2.get_archive_keys(r2, paths.construct_archive_path(TAG), output_key, ".zip")
    if not keys:
        print(f"[{TAG}/{label}] no new files, skipping")
        return

    datetimes: list[datetime] = []
    values: list[float] = []
    for key in keys:
        with zipfile.ZipFile(io.BytesIO(R2.download_bytes(r2, key))) as zf:
            for name in zf.namelist():
                if file_re.search(name):
                    for e in json.loads(zf.read(name)):
                        dt = _parse_datetime(e.get(date_field, ""))
                        if dt is not None:
                            datetimes.append(dt)
                            values.append(float(e.get(value_field, 0)))

    df = (
        pl.DataFrame(
            {"datetime": datetimes, "value": values},
            schema={"datetime": pl.Datetime, "value": pl.Float64},
        )
        .with_columns(pl.col("datetime").dt.date().alias("date"))
        .select(["datetime", "date", "value"])
        .sort("datetime")
    )

    R2.store_parquet(r2, output_key, df, sort_col="datetime", overwrite=True)
    print(f"[{TAG}/{label}] {len(df)} rows")


def _parse_datetime(s: str) -> datetime | None:
    s = s.strip()
    for fmt, length in [("%Y-%m-%dT%H:%M:%S", 19), ("%Y-%m-%d %H:%M:%S", 19), ("%m/%d/%y", 8)]:
        try:
            return datetime.strptime(s[:length], fmt)
        except ValueError:
            pass
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d")
    except ValueError:
        return None
