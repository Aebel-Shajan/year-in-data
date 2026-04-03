"""
Bronze asset: fitbit

Archives any raw files waiting in the inbox to the dated bronze store.
Users upload Fitbit Google Takeout ZIPs manually to the inbox.
"""

from __future__ import annotations

from pipeline import r2 as R2
from pipeline.config import Config, Secrets
from pipeline.r2 import R2Client

SOURCE = "fitbit"


def materialize(r2: R2Client, secrets: Secrets | None = None, config: Config | None = None) -> None:  # noqa: ARG001
    keys = R2.list_keys(r2, R2.inbox_prefix(SOURCE))
    if not keys:
        print(f"[bronze/{SOURCE}] inbox empty, skipping")
        return
    R2.archive_inbox(r2, SOURCE)
    print(f"[bronze/{SOURCE}] archived {len(keys)} file(s)")
