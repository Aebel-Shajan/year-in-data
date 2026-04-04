"""
Bronze asset: fitbit

Archives any raw files waiting in the inbox to the dated bronze store.
Users upload Fitbit Google Takeout ZIPs manually to the inbox.
"""

from __future__ import annotations

from pipeline import r2 as R2
from pipeline.config import PipelineConfig
from pipeline.r2 import R2Client


def fitbit_zip(r2: R2Client, input_key: str, output_key: str, config: PipelineConfig | None = None) -> None:  # noqa: ARG001
    keys = R2.list_keys(r2, input_key + "/")
    if not keys:
        print(f"[{output_key}] inbox empty, skipping")
        return
    R2.archive_inbox(r2, input_key, output_key)
    print(f"[{output_key}] archived {len(keys)} file(s)")
