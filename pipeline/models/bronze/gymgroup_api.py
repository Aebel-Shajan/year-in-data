"""
Bronze asset: gymgroup/checkins

When runtime_env is "local", fetches full check-in history from The Gym Group
API and saves it to the inbox. Otherwise expects the inbox to be pre-populated
by a separate workflow.

Then archives any inbox files to the bronze store.

Bronze JSON format: [{checkInDate, gymLocationName, duration, ...}, ...]
"""

from __future__ import annotations

import json
from datetime import date

import httpx

from pipeline import r2 as R2
from pipeline.config import Config, Secrets
from pipeline.r2 import R2Client

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


def gymgroup_api(r2: R2Client, input_key: str, output_key: str, secrets: Secrets | None = None, config: Config | None = None) -> None:
    assert secrets and config, "gymgroup bronze requires secrets and config"
    if config.runtime_env == "local":
        check_ins = _fetch(secrets.gym_group_username, secrets.gym_group_password)
        if check_ins:
            filename = f"checkins_{date.today().isoformat()}.json"
            R2.upload_bytes(r2, input_key + "/" + filename, json.dumps(check_ins).encode(), "application/json")

    keys = R2.list_keys(r2, input_key + "/")
    if not keys:
        print(f"[{output_key}] inbox empty, skipping")
        return
    R2.archive_inbox(r2, input_key, output_key)
    print(f"[{output_key}] archived {len(keys)} file(s)")


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
