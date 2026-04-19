"""
Source: gymgroup

Processes inbox files containing Gym Group check-in history.
Fetch data first with: uv run python scripts/sync_api.py
"""

from __future__ import annotations

import json
from datetime import date

import httpx
import polars as pl

from pipeline.common import r2 as R2
from pipeline.common.config import PipelineConfig
from pipeline.common import paths
from pipeline.common.paths import Source, Table
from pipeline.common.r2 import R2Client

TAG = Source.GYMGROUP

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

def fetch(r2: R2Client, config: PipelineConfig) -> None:
    """Fetch from Gym Group API and upload to inbox."""
    check_ins = _fetch_api(config.secrets.gym_group_username, config.secrets.gym_group_password)
    if check_ins:
        filename = f"checkins_{date.today().isoformat()}.json"
        R2.upload_bytes(r2, paths.inbox(TAG) + "/" + filename, json.dumps(check_ins).encode(), "application/json")
        print(f"[{TAG}] {len(check_ins)} check-ins → inbox")
    else:
        print(f"[{TAG}] no check-ins found")


def extract_gymgroup(r2: R2Client, config: PipelineConfig) -> None:
    R2.flush_inbox(r2, TAG, paths.inbox(TAG), paths.archive(TAG))

    archive_keys = R2.get_archive_keys(r2, paths.archive(TAG), paths.table(Table.GYMGROUP_VISITS), ".json")
    if not archive_keys:
        print(f"[{TAG}] no new files, skipping")
        return

    all_check_ins: list[dict] = []
    for key in archive_keys:
        all_check_ins.extend(json.loads(R2.download_bytes(r2, key)))

    df = (
        pl.DataFrame(all_check_ins)
        .select(["checkInDate", "gymLocationName", "duration"])
        .filter(pl.col("duration") > 0)
        .with_columns(
            pl.col("checkInDate").str.slice(0, 10).str.to_date("%Y-%m-%d").alias("date"),
            pl.col("gymLocationName").alias("category"),
            pl.col("duration").cast(pl.Float64).alias("duration_ms"),
        )
        .select(["date", "category", "duration_ms"])
        .group_by(["date", "category"])
        .agg(pl.col("duration_ms").sum())
        .sort("date")
    )

    R2.store_parquet(r2, paths.table(Table.GYMGROUP_VISITS), df, sort_col="date", overwrite=True)
    print(f"[{TAG}] {len(df)} rows")


def _fetch_api(username: str, password: str) -> list[dict]:
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
