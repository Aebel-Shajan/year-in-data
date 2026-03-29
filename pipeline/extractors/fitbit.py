"""
Fitbit extractor.

Upload a Google Takeout zip to: raw/fitbit/inbox/

The zip contains files like:
  Takeout/Fitbit/Global Export Data/calories-YYYY-MM-DD.json
  Takeout/Fitbit/Global Export Data/sleep-YYYY-MM-DD.json
  Takeout/Fitbit/Global Export Data/steps-YYYY-MM-DD.json
  Takeout/Fitbit/Global Export Data/exercise-YYYY-MM-DD.json

Each file is a list of intraday readings for one day.
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

_FILE_RE = re.compile(
    r"Fitbit/Global Export Data/(calories|sleep|steps|exercise)-(\d{4}-\d{2}-\d{2})\.json$",
    re.IGNORECASE,
)

# (unit, human label) per metric
METRICS: dict[str, tuple[str, str]] = {
    "calories": ("kcal", "Calories burned"),
    "sleep":    ("hours", "Sleep duration"),
    "steps":    ("steps", "Steps"),
    "exercise": ("minutes", "Active minutes"),
}


def run(r2: R2Client) -> None:
    inbox = R2.inbox_prefix("fitbit")
    zip_keys = [k for k in R2.list_keys(r2, inbox) if k.endswith(".zip")]

    if not zip_keys:
        print("[fitbit] inbox is empty, skipping")
        return

    frames = _extract(r2, zip_keys)

    for metric, df in frames.items():
        print(f"[fitbit/{metric}] {len(df)} rows")
        unit, label = METRICS[metric]
        R2.store_partitions(r2, "fitbit", metric, df)
        R2.write_web_json(r2, "fitbit", metric, unit, label)

    R2.archive_inbox(r2, "fitbit")


def _extract(r2_client: R2Client, zip_keys: list[str]) -> dict[str, pl.DataFrame]:
    rows: dict[str, list[dict]] = {m: [] for m in METRICS}

    for key in zip_keys:
        print(f"[fitbit] reading {key}")
        data = R2.download_bytes(r2_client, key)
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            for name in zf.namelist():
                m = _FILE_RE.search(name)
                if not m:
                    continue
                metric = m.group(1).lower()
                if metric not in rows:
                    continue
                entries: list[dict] = json.loads(zf.read(name))
                rows[metric].extend(_aggregate_entries(metric, entries))

    return {metric: _to_df(r) for metric, r in rows.items() if r}


def _parse_date(s: str) -> date | None:
    """Parse a date from either 'YYYY-MM-DD ...' or 'MM/DD/YY ...' formats."""
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%y"):
        try:
            return datetime.strptime(s[:8 if "/" in s else 10], fmt).date()
        except ValueError:
            continue
    return None


def _aggregate_entries(metric: str, entries: list[dict]) -> list[dict]:
    """
    Convert raw entries from a (possibly multi-day) Takeout file into
    per-day rows, using the actual date embedded in each entry.
    """
    by_date: dict[date, float] = {}

    if metric in ("calories", "steps"):
        # Each entry: {"dateTime": "YYYY-MM-DD HH:MM:SS" or "MM/DD/YY H:MM", "value": "123"}
        for e in entries:
            d = _parse_date(e.get("dateTime", ""))
            if d is None:
                continue
            by_date[d] = by_date.get(d, 0.0) + float(e.get("value", 0))

    elif metric == "sleep":
        # Each entry: {"dateOfSleep": "YYYY-MM-DD", "minutesAsleep": 360, ...}
        for e in entries:
            d = _parse_date(e.get("dateOfSleep", ""))
            if d is None:
                continue
            by_date[d] = by_date.get(d, 0.0) + int(e.get("minutesAsleep", 0)) / 60

    elif metric == "exercise":
        # Each entry is a workout with "startTime": "YYYY-MM-DDTHH:MM:SS" or "MM/DD/YY H:MM"
        for e in entries:
            d = _parse_date(e.get("startTime", ""))
            if d is None:
                continue
            by_date[d] = by_date.get(d, 0.0) + int(e.get("activeDuration", 0)) / 60_000

    return [{"date": d, "value": round(v, 2)} for d, v in by_date.items()]


def _to_df(rows: list[dict]) -> pl.DataFrame:
    return (
        pl.DataFrame(
            {"date": [r["date"] for r in rows], "value": [r["value"] for r in rows]},
            schema={"date": pl.Date, "value": pl.Float64},
        )
        .group_by("date")
        .agg(pl.col("value").sum())
        .sort("date")
    )
