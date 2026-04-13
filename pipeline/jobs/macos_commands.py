"""
Source: macos_commands

Parses ~/.zsh_history for command stems. Always runs locally.
"""

from __future__ import annotations

import json
import re
from datetime import date, datetime, timezone
from pathlib import Path

import polars as pl

from pipeline import paths, r2 as R2
from pipeline.config import PipelineConfig
from pipeline.paths import Source, Table
from pipeline.r2 import R2Client

TAG = Source.MACOS_COMMANDS

_HISTORY_FILE = Path.home() / ".zsh_history"
_LINE_RE = re.compile(r"^: (\d+):\d+;(.+)$")

def fetch(r2: R2Client, config: PipelineConfig) -> None:
    """Parse ~/.zsh_history and upload to inbox."""
    records = _parse_history()
    if not records:
        print(f"[{TAG}] no commands found, skipping")
        return
    filename = f"commands_{date.today().isoformat()}.json"
    R2.upload_bytes(r2, paths.inbox(TAG) + "/" + filename, json.dumps(records).encode(), "application/json")
    print(f"[{TAG}] {len(records)} commands → inbox")


def run_job(r2: R2Client, config: PipelineConfig) -> None:
    fetch(r2, config)

    R2.flush_inbox(r2, TAG, paths.inbox(TAG), paths.archive(TAG))

    archive_keys = R2.get_archive_keys(r2, paths.archive(TAG), paths.table(Table.MACOS_COMMANDS), ".json")
    if not archive_keys:
        print(f"[{TAG}] no new files, skipping")
        return

    all_records: list[dict] = []
    for key in archive_keys:
        all_records.extend(json.loads(R2.download_bytes(r2, key)))

    df = (
        pl.DataFrame(
            {
                "date": [date.fromisoformat(r["date"]) for r in all_records],
                "category": [r["command"] for r in all_records],
            },
            schema={"date": pl.Date, "category": pl.Utf8},
        )
        .with_columns(pl.lit(1).cast(pl.Int64).alias("count"))
        .group_by(["date", "category"])
        .agg(pl.col("count").sum())
        .sort("date")
    )

    R2.store_parquet(r2, paths.table(Table.MACOS_COMMANDS), df, sort_col="date", overwrite=True)
    print(f"[{TAG}] {len(df)} rows")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_history(path: Path = _HISTORY_FILE) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"zsh history not found at {path}")

    records: list[dict] = []
    text = path.read_bytes().decode("utf-8", errors="replace")
    for line in text.splitlines():
        m = _LINE_RE.match(line)
        if not m:
            continue
        ts = int(m.group(1))
        command = m.group(2).split()[0]
        day = datetime.fromtimestamp(ts, tz=timezone.utc).date()
        records.append({"date": day.isoformat(), "command": command})
    return records
