"""
Bronze asset: zsh_history/commands

Parses ~/.zsh_history, saves raw (date, command_stem) pairs to the inbox,
then archives them to the bronze store. Only the first word of each command
is captured to avoid storing secrets or arguments.

Bronze JSON format: [{date, command}, ...]
"""

from __future__ import annotations

import json
import re
from datetime import date, datetime, timezone
from pathlib import Path

from pipeline import r2 as R2
from pipeline.config import Config, Secrets
from pipeline.r2 import R2Client

SOURCE = "zsh_history"

_HISTORY_FILE = Path.home() / ".zsh_history"
_LINE_RE = re.compile(r"^: (\d+):\d+;(.+)$")


def materialize(r2: R2Client, secrets: Secrets | None = None, config: Config | None = None) -> None:  # noqa: ARG001
    records = _parse_history()
    if not records:
        print(f"[bronze/{SOURCE}] no data found, skipping")
        return

    filename = f"commands_{date.today().isoformat()}.json"
    R2.upload_bytes(r2, R2.inbox_prefix(SOURCE) + filename, json.dumps(records).encode(), "application/json")
    R2.archive_inbox(r2, SOURCE)
    print(f"[bronze/{SOURCE}] {len(records)} commands → archived")


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
