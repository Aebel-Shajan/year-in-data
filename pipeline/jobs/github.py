"""
Source: github

Processes inbox files containing GitHub contribution data.
Fetch data first with: uv run python scripts/sync_api.py
"""

from __future__ import annotations

import json
import os
from datetime import date, timedelta, timezone
from datetime import datetime as dt

import httpx
import polars as pl

from pipeline import paths, r2 as R2
from pipeline.config import PipelineConfig
from pipeline.paths import Source, Table
from pipeline.r2 import R2Client

TAG = Source.GITHUB

_DEFAULT_API_URL = "https://api.github.com/graphql"

_GQL = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""

def fetch(r2: R2Client, config: PipelineConfig) -> None:
    """Fetch from GitHub API and upload to inbox."""
    days = _fetch_api(config)
    if days:
        filename = f"contributions_{date.today().isoformat()}.json"
        R2.upload_bytes(r2, paths.inbox(TAG) + "/" + filename, json.dumps(days).encode(), "application/json")
        print(f"[{TAG}] {len(days)} contribution days → inbox")
    else:
        print(f"[{TAG}] no contributions found")


def process_github(r2: R2Client, config: PipelineConfig) -> None:
    R2.flush_inbox(r2, TAG, paths.inbox(TAG), paths.archive(TAG))

    archive_keys = sorted(R2.get_archive_keys(r2, paths.archive(TAG), paths.table(Table.GITHUB_CONTRIBUTIONS), ".json"))
    if not archive_keys:
        print(f"[{TAG}] no new files, skipping")
        return

    all_days: list[dict] = []
    for key in archive_keys:
        all_days.extend(json.loads(R2.download_bytes(r2, key)))

    df = (
        pl.DataFrame(
            {
                "date": [date.fromisoformat(d["date"]) for d in all_days],
                "value": [float(d["contributionCount"]) for d in all_days],
            },
            schema={"date": pl.Date, "value": pl.Float64},
        )
        .sort("date")
        .unique(subset=["date"], keep="last")
        .sort("date")
    )

    R2.store_parquet(r2, paths.table(Table.GITHUB_CONTRIBUTIONS), df, sort_col="date", overwrite=True)
    print(f"[{TAG}] {len(df)} rows")


# ── Aggregation ───────────────────────────────────────────────────────────────

def aggregate(df: pl.DataFrame) -> pl.DataFrame:
    return df  # already one row per date


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fetch_api(config: PipelineConfig) -> list[dict]:
    api_url = os.getenv("GITHUB_API_URL", _DEFAULT_API_URL)
    end = dt.now(tz=timezone.utc)
    start = end - timedelta(weeks=52)

    resp = httpx.post(
        api_url,
        json={
            "query": _GQL,
            "variables": {
                "login": config.github_username,
                "from": start.isoformat(),
                "to": end.isoformat(),
            },
        },
        headers={
            "Authorization": f"bearer {config.secrets.github_token}",
            "Content-Type": "application/json",
        },
        timeout=30,
    )
    resp.raise_for_status()

    weeks = (
        resp.json()["data"]["user"]["contributionsCollection"]
        ["contributionCalendar"]["weeks"]
    )
    return [
        {"date": day["date"], "contributionCount": day["contributionCount"]}
        for week in weeks
        for day in week["contributionDays"]
        if day["contributionCount"] > 0
    ]
