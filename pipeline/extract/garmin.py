"""
Source: garmin

Fetches daily wellness summaries and activities from Garmin Connect.
Requires GARMIN_USERNAME and GARMIN_PASSWORD in env / .env.
"""

from __future__ import annotations

from datetime import date, timedelta

import polars as pl
from garminconnect import Garmin

from pipeline.common import paths, r2 as R2
from pipeline.common.config import PipelineConfig
from pipeline.common.paths import Source, Table
from pipeline.common.r2 import R2Client

TAG = Source.GARMIN


def fetch(r2: R2Client, config: PipelineConfig) -> None:
    client = _login(config)
    _store_wellness(r2, client)
    _store_activities(r2, client)


# ── Pure functions ─────────────────────────────────────────────────────────────

def parse_wellness(stats: list[dict]) -> pl.DataFrame:
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
        for s in stats
        if s.get("calendarDate")
    ]
    return (
        pl.DataFrame(rows)
        .with_columns(pl.col("date").str.to_date("%Y-%m-%d"))
        .sort("date")
    )


def parse_activities(activities: list[dict]) -> pl.DataFrame:
    rows = [
        {
            "activity_id":   str(a.get("activityId", "")),
            "date":          (a.get("startTimeLocal") or "")[:10],
            "name":          a.get("activityName", ""),
            "type":          (a.get("activityType") or {}).get("typeKey", ""),
            "duration_sec":  a.get("duration", 0.0),
            "distance_m":    a.get("distance", 0.0),
            "calories":      a.get("calories", 0.0),
        }
        for a in activities
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


def _store_wellness(r2: R2Client, client: Garmin) -> None:
    today = date.today()
    stats = []
    for i in range(365):
        d = (today - timedelta(days=i)).isoformat()
        s = client.get_stats(d)
        if s:
            stats.append(s)

    df = parse_wellness(stats)
    R2.store_parquet(r2, paths.construct_table_path(Table.GARMIN_WELLNESS), df, sort_col="date", dedup_cols=["date"], overwrite=True)
    print(f"[{TAG}/wellness] {len(df)} rows")


def _store_activities(r2: R2Client, client: Garmin) -> None:
    activities = client.get_activities(0, 1000)
    df = parse_activities(activities)
    R2.store_parquet(r2, paths.construct_table_path(Table.GARMIN_ACTIVITIES), df, sort_col="date", dedup_cols=["activity_id"], overwrite=True)
    print(f"[{TAG}/activities] {len(df)} rows")
