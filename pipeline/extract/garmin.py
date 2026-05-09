"""
Source: garmin

Processes inbox files containing Garmin Connect data.
Fetch data first with: uv run python scripts/sync_api.py
"""

from __future__ import annotations

import json
import re
from datetime import date, timedelta

import polars as pl
from garminconnect import Garmin

from pipeline.common import paths, r2 as R2
from pipeline.common.config import PipelineConfig
from pipeline.common.paths import Source, Table
from pipeline.common.r2 import R2Client

TAG = Source.GARMIN

_WELLNESS_RE   = re.compile(r"wellness-\d{4}-\d{2}-\d{2}\.json$")
_ACTIVITIES_RE = re.compile(r"activities-\d{4}-\d{2}-\d{2}\.json$")


def fetch(r2: R2Client, config: PipelineConfig) -> None:
    """Fetch from Garmin Connect API and upload to inbox."""
    client = _login(config)
    today = date.today().isoformat()

    wellness = _fetch_wellness(client)
    R2.upload_bytes(r2, f"{paths.construct_inbox_path(TAG)}/wellness-{today}.json", json.dumps(wellness).encode(), "application/json")
    print(f"[{TAG}] {len(wellness)} wellness days → inbox")

    activities = _fetch_activities(client)
    R2.upload_bytes(r2, f"{paths.construct_inbox_path(TAG)}/activities-{today}.json", json.dumps(activities).encode(), "application/json")
    print(f"[{TAG}] {len(activities)} activities → inbox")


def extract_garmin(r2: R2Client, config: PipelineConfig) -> None:
    R2.flush_inbox(r2, TAG, paths.construct_inbox_path(TAG), paths.construct_archive_path(TAG))

    _extract_table(r2, paths.construct_table_path(Table.GARMIN_WELLNESS),   _WELLNESS_RE,   parse_wellness)
    _extract_table(r2, paths.construct_table_path(Table.GARMIN_ACTIVITIES), _ACTIVITIES_RE, parse_activities)


# ── Pure functions ─────────────────────────────────────────────────────────────

def parse_wellness(records: list[dict]) -> pl.DataFrame:
    rows = [
        {
            "date":            s.get("calendarDate"),
            "steps":           s.get("totalSteps"),
            "distance_m":      s.get("totalDistanceMeters"),
            "calories":        s.get("totalKilocalories"),
            "active_calories": s.get("activeKilocalories"),
            "resting_hr":      s.get("restingHeartRate"),
            "avg_stress":      s.get("averageStressLevel"),
            "sleep_seconds":   s.get("sleepingSeconds"),
            "floors_ascended": s.get("floorsAscended"),
        }
        for s in records
        if s.get("calendarDate")
    ]
    return (
        pl.DataFrame(rows)
        .with_columns(pl.col("date").str.to_date("%Y-%m-%d"))
        .sort("date")
    )


def parse_activities(records: list[dict]) -> pl.DataFrame:
    rows = [
        {
            "activity_id":  str(a.get("activityId", "")),
            "date":         (a.get("startTimeLocal") or "")[:10],
            "name":         a.get("activityName", ""),
            "type":         (a.get("activityType") or {}).get("typeKey", ""),
            "duration_sec": a.get("duration", 0.0),
            "distance_m":   a.get("distance", 0.0),
            "calories":     a.get("calories", 0.0),
        }
        for a in records
        if a.get("activityId")
    ]
    return (
        pl.DataFrame(rows)
        .with_columns(pl.col("date").str.to_date("%Y-%m-%d"))
        .sort("date")
    )


# ── Imperative shell ───────────────────────────────────────────────────────────

def _login(config: PipelineConfig) -> Garmin:
    client = Garmin(config.secrets.garmin_username, config.secrets.garmin_password)
    client.login()
    return client


def _fetch_wellness(client: Garmin) -> list[dict]:
    today = date.today()
    stats = []
    for i in range(365):
        d = (today - timedelta(days=i)).isoformat()
        s = client.get_stats(d)
        if s:
            stats.append(s)
    return stats


def _fetch_activities(client: Garmin) -> list[dict]:
    return client.get_activities(0, 1000)


def _extract_table(r2: R2Client, output_key: str, file_re: re.Pattern, parse_fn) -> None:
    label = output_key.split("/")[-1].removesuffix(".parquet")
    keys = R2.get_archive_keys(r2, paths.construct_archive_path(TAG), output_key, ".json")
    matched = [k for k in keys if file_re.search(k)]
    if not matched:
        print(f"[{TAG}/{label}] no new files, skipping")
        return

    records: list[dict] = []
    for key in matched:
        records.extend(json.loads(R2.download_bytes(r2, key)))

    df = parse_fn(records)
    dedup = ["date"] if "activity_id" not in df.columns else ["activity_id"]
    R2.store_parquet(r2, output_key, df, sort_col="date", dedup_cols=dedup, overwrite=True)
    print(f"[{TAG}/{label}] {len(df)} rows")
