"""
Bronze asset: macos/screentime

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

_DB = Path.home() / "Library/Application Support/Knowledge/knowledgeC.db"

_QUERY = """
SELECT
    ZOBJECT.ZVALUESTRING                        AS app,
    (ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE)     AS usage_secs,
    (ZOBJECT.ZSTARTDATE + 978307200)            AS start_unix,
    ZOBJECT.ZSECONDSFROMGMT                     AS tz_offset
FROM
    ZOBJECT
    LEFT JOIN ZASSET_NAME ON ZOBJECT.ZASSET_NAME = ZASSET_NAME.Z_PK
WHERE
    ZSTREAMNAME = '/app/usage'
    AND ZOBJECT.ZVALUESTRING IS NOT NULL
    AND (ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE) > 0
ORDER BY
    ZOBJECT.ZSTARTDATE DESC
"""


def macos_screentime(r2: R2Client, input_key: str, output_key: str, secrets: Secrets | None = None, config: Config | None = None) -> None:  # noqa: ARG001
    if config and config.runtime_env == "local":
        records = _query_db()
        filename = f"screentime_{date.today().isoformat()}.json"
        R2.upload_bytes(r2, input_key + "/" + filename, json.dumps(records).encode(), "application/json")

    keys = R2.list_keys(r2, input_key + "/")
    if not keys:
        print(f"[{output_key}] inbox empty, skipping")
        return
    R2.archive_inbox(r2, input_key, output_key)
    print(f"[{output_key}] archived {len(keys)} file(s)")


def _query_db(db_path: Path = _DB) -> list[dict]:
    if not db_path.exists():
        raise FileNotFoundError(f"knowledgeC.db not found at {db_path}")
    if not os.access(db_path, os.R_OK):
        raise PermissionError(
            f"{db_path} is not readable. "
            "Grant Full Disk Access to your terminal in "
            "System Settings → Privacy & Security → Full Disk Access"
        )
    with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as con:
        rows = con.execute(_QUERY).fetchall()
        return [
            {"app": app, "usage_secs": secs, "start_unix": unix, "tz_offset": tz or 0}
            for app, secs, unix, tz in rows
        ]
