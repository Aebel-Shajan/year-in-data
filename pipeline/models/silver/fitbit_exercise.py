"""Silver table: fitbit/exercise — (date, value) value = active duration ms"""

from __future__ import annotations

import io
import json
import re
import zipfile
from datetime import date, datetime

import polars as pl

from pipeline import r2 as R2
from pipeline.r2 import R2Client

_FILE_RE = re.compile(r"Fitbit/Global Export Data/exercise-\d{4}-\d{2}-\d{2}\.json$", re.IGNORECASE)


def fitbit_exercise(r2: R2Client, input_key: str, output_key: str, start: date | None = None, end: date | None = None) -> None:
    start = start or R2.latest_date(r2, output_key)
    keys = [k for k in R2.list_bronze_keys(r2, input_key, start=start, end=end) if k.endswith(".zip")]
    if not keys:
        print(f"[{output_key.removesuffix('.parquet')}] no archived files found, skipping")
        return

    entries: list[dict] = []
    for key in keys:
        with zipfile.ZipFile(io.BytesIO(R2.download_bytes(r2, key))) as zf:
            for name in zf.namelist():
                if _FILE_RE.search(name):
                    entries.extend(json.loads(zf.read(name)))

    by_date: dict[date, float] = {}
    for e in entries:
        d = _parse_date(e.get("startTime", ""))
        if d is not None:
            by_date[d] = by_date.get(d, 0.0) + float(e.get("activeDuration", 0))

    dates, values = zip(*by_date.items()) if by_date else ([], [])
    df = pl.DataFrame(
        {"date": list(dates), "value": list(values)},
        schema={"date": pl.Date, "value": pl.Float64},
    ).sort("date")

    R2.store_parquet(r2, output_key, df, sort_col="date", overwrite=True)
    print(f"[{output_key.removesuffix('.parquet')}] {len(df)} rows")


def _parse_date(s: str) -> date | None:
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%y"):
        try:
            return datetime.strptime(s[:8 if "/" in s else 10], fmt).date()
        except ValueError:
            continue
    return None
