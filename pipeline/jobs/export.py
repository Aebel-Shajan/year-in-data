"""
Export daily Parquet files to the public web bucket as JSON.
"""

from __future__ import annotations

import io
import json
from dataclasses import dataclass
from datetime import date

import polars as pl

from pipeline.common import r2 as R2
from pipeline.common.config import PipelineConfig
from pipeline.common import paths
from pipeline.common.paths import Table
from pipeline.common.r2 import R2Client, upload_bytes


@dataclass(frozen=True)
class ExportSpec:
    table: Table
    unit: str
    label: str


_EXPORTS: list[ExportSpec] = [
    ExportSpec(Table.DAILY_FITBIT_CALORIES,      "kcal",    "Calories burned"),
    ExportSpec(Table.DAILY_FITBIT_EXERCISE,      "minutes", "Active minutes"),
    ExportSpec(Table.DAILY_FITBIT_SLEEP,         "hours",   "Sleep duration"),
    ExportSpec(Table.DAILY_FITBIT_STEPS,         "steps",   "Steps"),
    ExportSpec(Table.DAILY_GITHUB_CONTRIBUTIONS, "commits", "GitHub contributions"),
    ExportSpec(Table.DAILY_GYMGROUP_VISITS,      "minutes", "Gym duration"),
    ExportSpec(Table.DAILY_KINDLE_READING,       "minutes", "Reading time"),
    ExportSpec(Table.DAILY_MACOS_COMMANDS,       "count",   "Shell commands"),
    ExportSpec(Table.DAILY_MACOS_SCREENTIME,     "minutes", "Screen time"),
    ExportSpec(Table.DAILY_STRONG_WORKOUTS,      "minutes", "Workout duration"),
]


def export_to_web(r2: R2Client, config: PipelineConfig) -> None:
    web_r2 = R2.make_web_client(config)
    for spec in _EXPORTS:
        daily_key = paths.construct_table_path(spec.table)
        _export_json(r2, web_r2, daily_key, f"daily_{spec.table}.json", spec.unit, spec.label)



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
