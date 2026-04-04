"""
Job: github

Fetches the last 52 weeks of contribution data via the GitHub GraphQL API
and saves the raw response as JSON to the bronze inbox.

Bronze JSON format: [{date, contributionCount}, ...]
"""

from __future__ import annotations

import json
import os
from datetime import date, timedelta, timezone
from datetime import datetime as dt

import httpx

from pipeline import r2 as R2
from pipeline.config import Config, Secrets
from pipeline.r2 import R2Client

ASSET_NAME = "github"

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


def run(r2: R2Client, secrets: Secrets, config: Config) -> None:
    days = _fetch(secrets, config)
    if not days:
        print(f"[jobs/{ASSET_NAME}] no contributions returned, skipping")
        return

    filename = f"contributions_{date.today().isoformat()}.json"
    R2.upload_bytes(r2, f"bronze/inbox/{ASSET_NAME}/{filename}", json.dumps(days).encode(), "application/json")
    print(f"[jobs/{ASSET_NAME}] {len(days)} days → inbox")


def _fetch(secrets: Secrets, config: Config) -> list[dict]:
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
    return [
        {"date": day["date"], "contributionCount": day["contributionCount"]}
        for week in weeks
        for day in week["contributionDays"]
        if day["contributionCount"] > 0
    ]
