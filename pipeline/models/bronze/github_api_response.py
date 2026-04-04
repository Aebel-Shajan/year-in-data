"""
Bronze asset: github/contributions

When runtime_env is "local", fetches the last 52 weeks of contribution data
via the GitHub GraphQL API and saves it to the inbox. Otherwise expects the
inbox to be pre-populated by a separate workflow.

Then archives any inbox files to the bronze store.

Bronze JSON format: [{date, contributionCount}, ...]
"""

from __future__ import annotations

import json
import os
from datetime import date, timedelta, timezone
from datetime import datetime as dt

import httpx

from pipeline import r2 as R2
from pipeline.config import PipelineConfig
from pipeline.r2 import R2Client

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


def github_api_response(r2: R2Client, input_key: str, output_key: str, config: PipelineConfig | None = None) -> None:
    assert config, "github bronze requires secrets and config"
    if config.runtime_env == "local":
        days = _fetch(config)
        if days:
            filename = f"contributions_{date.today().isoformat()}.json"
            R2.upload_bytes(r2, input_key + "/" + filename, json.dumps(days).encode(), "application/json")

    keys = R2.list_keys(r2, input_key + "/")
    if not keys:
        print(f"[{output_key}] inbox empty, skipping")
        return
    R2.archive_inbox(r2, input_key, output_key)
    print(f"[{output_key}] archived {len(keys)} file(s)")


def _fetch(config: PipelineConfig) -> list[dict]:
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
