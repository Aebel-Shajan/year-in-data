"""
The Gym Group extractor.

Fetches gym visit check-in history directly from The Gym Group API.

Requires GYM_GROUP_USERNAME and GYM_GROUP_PASSWORD in the environment.

Each check-in has:
  checkInDate    — local ISO datetime (Europe/London)
  gymLocationName — gym branch name (used as category)
  duration       — session length in milliseconds
"""

from __future__ import annotations

import httpx
import polars as pl

from pipeline import r2 as R2
from pipeline.r2 import R2Client

METRIC = "visits"
UNIT = "minutes"
LABEL = "Gym duration"

_BASE = "https://thegymgroup.netpulse.com/np"
_HEADERS = {
    "accept": "application/json",
    "accept-encoding": "gzip",
    "connection": "Keep-Alive",
    "host": "thegymgroup.netpulse.com",
    "x-np-user-agent": (
        "clientType=MOBILE_DEVICE; devicePlatform=ANDROID; deviceUid=; "
        "applicationName=The Gym Group; applicationVersion=5.0; applicationVersionCode=38"
    ),
}


def run(r2: R2Client, username: str, password: str) -> None:
    check_ins = _fetch(username, password)
    if not check_ins:
        print("[gymgroup] no check-ins returned, skipping")
        return

    df = _to_df(check_ins)
    print(f"[gymgroup/{METRIC}] {len(df)} rows")
    R2.store_partitions(r2, "gymgroup", METRIC, df)
    R2.write_web_json(r2, "gymgroup", METRIC, UNIT, LABEL)


def _fetch(username: str, password: str) -> list[dict]:
    with httpx.Client(headers=_HEADERS) as client:
        resp = client.post(
            f"{_BASE}/exerciser/login",
            data={"username": username, "password": password},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )
        resp.raise_for_status()
        user_id = resp.json()["uuid"]
        cookie = resp.headers.get("set-cookie", "")

        visits = client.get(
            f"{_BASE}/exercisers/{user_id}/check-ins/history",
            params={"endDate": "2099-01-01T00:00:00"},
            headers={"cookie": cookie},
        )
        visits.raise_for_status()
        return visits.json().get("checkIns", [])


def _to_df(check_ins: list[dict]) -> pl.DataFrame:
    return (
        pl.DataFrame(check_ins)
        .select(["checkInDate", "gymLocationName", "duration"])
        .filter(pl.col("duration") > 0)
        .with_columns(
            pl.col("checkInDate").str.slice(0, 10).str.to_date("%Y-%m-%d").alias("date"),
            (pl.col("duration").cast(pl.Float64) / 60_000).round(1).alias("value"),
            pl.col("gymLocationName").alias("category"),
        )
        .select(["date", "value", "category"])
        .sort("date")
    )
