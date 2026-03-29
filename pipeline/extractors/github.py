"""
GitHub contributions extractor.

Fetches the last 52 weeks of contribution data via the GitHub GraphQL API.
No manual upload needed — runs automatically.
"""

from __future__ import annotations

from datetime import date, timedelta, timezone
from datetime import datetime as dt

import httpx
import polars as pl

from pipeline import r2 as R2
from pipeline.config import Config, Secrets
from pipeline.r2 import R2Client

METRIC = "contributions"
UNIT = "commits"
LABEL = "GitHub contributions"
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


def run(r2: R2Client, secrets: Secrets, config: Config, api_url: str = _DEFAULT_API_URL) -> None:
    df = _fetch(secrets, config, api_url)
    print(f"[github/{METRIC}] {len(df)} rows")
    R2.store_partitions(r2, "github", METRIC, df)
    R2.write_web_json(r2, "github", METRIC, UNIT, LABEL)
    # No inbox to archive for GitHub


def _fetch(secrets: Secrets, config: Config, api_url: str = _DEFAULT_API_URL) -> pl.DataFrame:
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
            "Authorization": f"bearer {secrets.github_token}",
            "Content-Type": "application/json",
        },
        timeout=30,
    )
    resp.raise_for_status()

    weeks = (
        resp.json()["data"]["user"]["contributionsCollection"]
        ["contributionCalendar"]["weeks"]
    )

    rows = [
        {
            "date": date.fromisoformat(day["date"]),
            "value": float(day["contributionCount"]),
        }
        for week in weeks
        for day in week["contributionDays"]
        if day["contributionCount"] > 0
    ]

    return pl.DataFrame(
        {"date": [r["date"] for r in rows], "value": [r["value"] for r in rows]},
        schema={"date": pl.Date, "value": pl.Float64},
    ).sort("date")
