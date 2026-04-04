"""
Bronze asset: strong/workouts

Archives any raw files waiting in the inbox to the dated bronze store.
Users upload Strong app CSV exports manually to the inbox.
"""

from __future__ import annotations

from pipeline import r2 as R2
from pipeline.config import Config, Secrets
from pipeline.r2 import R2Client


def strong_csv(r2: R2Client, input_key: str, output_key: str, secrets: Secrets | None = None, config: Config | None = None) -> None:  # noqa: ARG001
    keys = R2.list_keys(r2, input_key + "/")
    if not keys:
        print(f"[{output_key}] inbox empty, skipping")
        return
    R2.archive_inbox(r2, input_key, output_key)
    print(f"[{output_key}] archived {len(keys)} file(s)")
