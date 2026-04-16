"""
Export daily Parquet files to the public web bucket as JSON.
"""

from __future__ import annotations

import io
import json
from datetime import date

import polars as pl

from pipeline import paths, r2 as R2
from pipeline.config import PipelineConfig
from pipeline.paths import Table
from pipeline.r2 import R2Client, upload_bytes

# (table, web_path, unit, label)
# web_path becomes "{web_path}.json" in the web bucket
_EXPORTS: list[tuple[Table, str, str]] = [
    (Table.FITBIT_CALORIES,                 "kcal",    "Calories burned"),
    (Table.FITBIT_EXERCISE,                 "minutes", "Active minutes"),
    (Table.FITBIT_SLEEP,                       "hours",   "Sleep duration"),
    (Table.FITBIT_STEPS,                       "steps",   "Steps"),
    (Table.GITHUB_CONTRIBUTIONS,       "commits", "GitHub contributions"),
    (Table.GYMGROUP_VISITS,                 "minutes", "Gym duration"),
    (Table.KINDLE_READING,                   "minutes", "Reading time"),
    (Table.MACOS_COMMANDS,          "count",   "Shell commands"),
    (Table.MACOS_SCREENTIME,     "minutes", "Screen time"),
    (Table.STRONG_WORKOUTS,                 "minutes", "Workout duration"),
]


def export_to_web(r2: R2Client, config: PipelineConfig) -> None:
    web_r2 = R2.make_web_client(config)
    for table_name, unit, label in _EXPORTS:
        daily_key = paths.table(f"daily_{table_name}")
        _export_json(r2, web_r2, daily_key, f"daily_{table_name}.json", unit, label)



def _export_json(
    r2: R2Client,
    web_r2: R2Client,
    daily_key: str,
    web_path: str,
    unit: str,
    label: str,
) -> None:
    """Read a daily Parquet from r2 and write aggregated JSON to web_r2.

    Output format:
    {
      "source": "fitbit", "metric": "calories", "unit": "kcal",
      "label": "Calories burned", "updated_at": "2025-01-20",
      "data": [{"date": "2025-01-01", "value": 2100.0}, ...]
    }
    """
    if not R2.exists(r2, daily_key):
        print(f"{daily_key} does not exist!")
        return

    full = pl.read_parquet(io.BytesIO(R2.download_bytes(r2, daily_key))).sort("date")

    records: list[dict] = []
    for row in full.iter_rows(named=True):
        entry: dict = {"date": str(row["date"]), "value": row["value"]}
        if row.get("category") is not None:
            entry["category"] = row["category"]
        if row.get("image_url") is not None:
            entry["image_url"] = row["image_url"]
        records.append(entry)

    payload = {
        "name": web_path.strip(".json"),
        "unit": unit,
        "label": label,
        "updated_at": str(date.today()),
        "data": records,
    }
    print(f"uploading {len(records)} to {web_path}")
    upload_bytes(web_r2, f"{web_path}", json.dumps(payload).encode(), "application/json")
