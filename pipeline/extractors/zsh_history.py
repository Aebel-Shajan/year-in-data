"""
Zsh history extractor.

Reads ~/.zsh_history, extracts the first word of each command (to avoid
capturing secrets or arguments), and uploads daily command counts to R2.

The zsh extended history format is:
  : <unix_timestamp>:<elapsed>;<command>

Lines without this prefix (e.g. from plain HISTFILE) are skipped.
"""

from __future__ import annotations

import re
from datetime import date, datetime, timezone
from pathlib import Path

import polars as pl

from pipeline import r2 as R2
from pipeline.r2 import R2Client

METRIC = "commands"
UNIT = "count"
LABEL = "Shell commands"

_HISTORY_FILE = Path.home() / ".zsh_history"

# : 1705071243:0;git status
_LINE_RE = re.compile(r"^: (\d+):\d+;(.+)$")


def run(r2: R2Client) -> None:
    rows = _parse_history()
    if not rows:
        print("[zsh_history] no data found, skipping")
        return

    df = _to_df(rows)
    print(f"[zsh_history/{METRIC}] {len(df)} rows")
    R2.store_partitions(r2, "zsh_history", METRIC, df)
    R2.write_web_json(r2, "zsh_history", METRIC, UNIT, LABEL)


def _parse_history(path: Path = _HISTORY_FILE) -> list[tuple[date, str]]:
    if not path.exists():
        raise FileNotFoundError(f"zsh history not found at {path}")

    rows: list[tuple[date, str]] = []
    # zsh_history may contain invalid utf-8 sequences — use latin-1 as a safe fallback
    text = path.read_bytes().decode("utf-8", errors="replace")
    for line in text.splitlines():
        m = _LINE_RE.match(line)
        if not m:
            continue
        ts = int(m.group(1))
        command = m.group(2).split()[0]  # first word only — avoids leaking args/secrets
        day = datetime.fromtimestamp(ts, tz=timezone.utc).date()
        rows.append((day, command))
    return rows


def _to_df(rows: list[tuple[date, str]]) -> pl.DataFrame:
    dates, commands = zip(*rows)
    return (
        pl.DataFrame(
            {"date": list(dates), "category": list(commands)},
            schema={"date": pl.Date, "category": pl.Utf8},
        )
        .with_columns(pl.lit(1).alias("value"))
        .group_by(["date", "category"])
        .agg(pl.col("value").sum().cast(pl.Float64))
        .sort("date")
    )
