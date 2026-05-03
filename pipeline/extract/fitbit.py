"""
Source: fitbit

Processes Fitbit Google Takeout ZIPs uploaded manually to the inbox.
Produces four metrics: calories, exercise, sleep, steps.
"""

from __future__ import annotations

import json
import re
import tempfile
import zipfile
from pathlib import Path

import polars as pl

from pipeline.common import r2 as R2
from pipeline.common.config import PipelineConfig
from pipeline.common import paths
from pipeline.common.paths import Source, Table
from pipeline.common.r2 import R2Client

TAG = Source.FITBIT

_CALORIES_RE = re.compile(r"Fitbit/Global Export Data/calories-\d{4}-\d{2}-\d{2}\.json$", re.IGNORECASE)
_EXERCISE_RE = re.compile(r"Fitbit/Global Export Data/exercise-\d{4}.json$", re.IGNORECASE)
_SLEEP_RE    = re.compile(r"Fitbit/Global Export Data/sleep-\d{4}-\d{2}-\d{2}\.json$",    re.IGNORECASE)
_STEPS_RE    = re.compile(r"Fitbit/Global Export Data/steps-\d{4}-\d{2}-\d{2}\.json$",    re.IGNORECASE)


def extract_fitbit(r2: R2Client, config: PipelineConfig) -> None:
    R2.flush_inbox(r2, TAG, paths.construct_inbox_path(TAG), paths.construct_archive_path(TAG))

    _store_metric(r2, paths.construct_table_path(Table.FITBIT_CALORIES), _CALORIES_RE, "dateTime",    "value")
    _store_metric(r2, paths.construct_table_path(Table.FITBIT_EXERCISE), _EXERCISE_RE, "startTime",   "activeDuration")
    _store_metric(r2, paths.construct_table_path(Table.FITBIT_SLEEP),    _SLEEP_RE,    "startTime", "minutesAsleep")
    _store_metric(r2, paths.construct_table_path(Table.FITBIT_STEPS),    _STEPS_RE,    "dateTime",    "value")


_DT_FORMATS = ["%m/%d/%y %H:%M:%S", "%y-%m-%dT%H:%M:00.000"]


def _parse_zip(path: Path, file_re: re.Pattern, date_field: str, value_field: str) -> pl.DataFrame:
    datetimes: list[str] = []
    values: list[float] = []
    with zipfile.ZipFile(path) as zf:
        for name in zf.namelist():
            if file_re.search(name):
                for entry in json.loads(zf.read(name)):
                    datetimes.append(entry.get(date_field, ""))
                    values.append(float(entry.get(value_field, 0)))

    return (
        pl.DataFrame({"datetime": datetimes, "value": values})
        .with_columns(
            pl.coalesce([
                pl.col("datetime").str.to_datetime(fmt, strict=False)
                for fmt in _DT_FORMATS
            ]).alias("datetime")
        )
        .drop_nulls("datetime")
        .with_columns(pl.col("datetime").dt.date().alias("date"))
        .select(["datetime", "date", "value"])
        .sort("datetime")
    )


def _store_metric(
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

    frames: list[pl.DataFrame] = []
    with tempfile.TemporaryDirectory() as tmp:
        for key in keys:
            path = Path(tmp) / Path(key).name
            path.write_bytes(R2.download_bytes(r2, key))
            frames.append(_parse_zip(path, file_re, date_field, value_field))

    df = pl.concat(frames)
    R2.store_parquet(r2, output_key, df, sort_col="datetime", dedup_cols=["datetime"], overwrite=True)
    print(f"[{TAG}/{label}] {len(df)} rows")
