"""
Silver tables: fitbit/*

Reads Fitbit Google Takeout ZIPs from the bronze inbox and produces four
silver tables — one per metric. All four are extracted in a single pass
since they come from the same ZIP files.

Silver schemas (all daily aggregates in source units):
  fitbit/calories  — (date, value)  value = kcal
  fitbit/sleep     — (date, value)  value = minutes asleep
  fitbit/steps     — (date, value)  value = step count
  fitbit/exercise  — (date, value)  value = active duration ms
"""

from __future__ import annotations

import io
import json
import re
import zipfile
from datetime import date, datetime

import polars as pl

from pipeline import r2 as R2
from pipeline.r2 import R2Client

SOURCE = "fitbit"

_METRICS = ("calories", "sleep", "steps", "exercise")

_FILE_RE = re.compile(
    r"Fitbit/Global Export Data/(calories|sleep|steps|exercise)-(\d{4}-\d{2}-\d{2})\.json$",
    re.IGNORECASE,
)


def materialize(r2: R2Client, start: date | None = None, end: date | None = None) -> None:
    keys = [k for k in R2.list_archived_keys(r2, SOURCE, start=start, end=end) if k.endswith(".zip")]
    if not keys:
        print(f"[silver/{SOURCE}] no archived files found, skipping")
        return

    by_metric: dict[str, list[dict]] = {m: [] for m in _METRICS}

    for key in keys:
        data = R2.download_bytes(r2, key)
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            for name in zf.namelist():
                m = _FILE_RE.search(name)
                if not m:
                    continue
                metric = m.group(1).lower()
                entries: list[dict] = json.loads(zf.read(name))
                by_metric[metric].extend(entries)

    for metric, entries in by_metric.items():
        if not entries:
            continue
        df = _aggregate(metric, entries)
        R2.store_parquet(r2, R2.silver_key(SOURCE, metric), df, sort_col="date", overwrite=True)
        print(f"[silver/{SOURCE}/{metric}] {len(df)} rows")


def _parse_date(s: str) -> date | None:
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%y"):
        try:
            return datetime.strptime(s[:8 if "/" in s else 10], fmt).date()
        except ValueError:
            continue
    return None


def _aggregate(metric: str, entries: list[dict]) -> pl.DataFrame:
    by_date: dict[date, float] = {}

    if metric in ("calories", "steps"):
        for e in entries:
            d = _parse_date(e.get("dateTime", ""))
            if d is None:
                continue
            by_date[d] = by_date.get(d, 0.0) + float(e.get("value", 0))

    elif metric == "sleep":
        for e in entries:
            d = _parse_date(e.get("dateOfSleep", ""))
            if d is None:
                continue
            by_date[d] = by_date.get(d, 0.0) + float(e.get("minutesAsleep", 0))

    elif metric == "exercise":
        for e in entries:
            d = _parse_date(e.get("startTime", ""))
            if d is None:
                continue
            by_date[d] = by_date.get(d, 0.0) + float(e.get("activeDuration", 0))

    dates, values = zip(*by_date.items()) if by_date else ([], [])
    return pl.DataFrame(
        {"date": list(dates), "value": list(values)},
        schema={"date": pl.Date, "value": pl.Float64},
    ).sort("date")
