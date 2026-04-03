"""
Bronze asset: screentime/app_usage

Queries knowledgeC.db, saves raw session rows to the inbox, then archives
them to the bronze store.

Bronze JSON format: [{app, usage_secs, start_unix, tz_offset}, ...]

Requires Full Disk Access for the terminal running this script:
  System Settings → Privacy & Security → Full Disk Access
"""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import date
from pathlib import Path

from pipeline import r2 as R2
from pipeline.config import Config, Secrets
from pipeline.r2 import R2Client

SOURCE = "screentime"

_DB = Path.home() / "Library/Application Support/Knowledge/knowledgeC.db"

_QUERY = """
SELECT
    ZOBJECT.ZVALUESTRING                        AS app,
    (ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE)     AS usage_secs,
    (ZOBJECT.ZSTARTDATE + 978307200)            AS start_unix,
    ZOBJECT.ZSECONDSFROMGMT                     AS tz_offset
FROM
    ZOBJECT
    LEFT JOIN ZSOURCE ON ZOBJECT.ZSOURCE = ZSOURCE.Z_PK
WHERE
    ZSTREAMNAME = '/app/usage'
    AND ZOBJECT.ZVALUESTRING IS NOT NULL
    AND (ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE) > 0
ORDER BY
    ZOBJECT.ZSTARTDATE DESC
"""


def materialize(r2: R2Client, secrets: Secrets | None = None, config: Config | None = None) -> None:  # noqa: ARG001
    rows = _query_db()
    if not rows:
        print(f"[bronze/{SOURCE}] no data returned, skipping")
        return

    records = [
        {"app": app, "usage_secs": secs, "start_unix": unix, "tz_offset": tz or 0}
        for app, secs, unix, tz in rows
    ]
    filename = f"app_usage_{date.today().isoformat()}.json"
    R2.upload_bytes(r2, R2.inbox_prefix(SOURCE) + filename, json.dumps(records).encode(), "application/json")
    R2.archive_inbox(r2, SOURCE)
    print(f"[bronze/{SOURCE}] {len(records)} rows → archived")


def _query_db(db_path: Path = _DB) -> list[tuple]:
    if not db_path.exists():
        raise FileNotFoundError(f"knowledgeC.db not found at {db_path}")
    if not os.access(db_path, os.R_OK):
        raise PermissionError(
            f"{db_path} is not readable. "
            "Grant Full Disk Access to your terminal in "
            "System Settings → Privacy & Security → Full Disk Access"
        )
    with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as con:
        return con.execute(_QUERY).fetchall()
