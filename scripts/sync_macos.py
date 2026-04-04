"""
Sync macOS Screen Time and shell history to the R2 bronze inbox.

Uploads today's data to the inbox so the main pipeline can later archive
and process it. Does not archive or run silver/gold stages.

Run on a cron schedule to keep the bronze inbox fresh:

  uv run python scripts/sync_macos.py

To run daily at 11pm via crontab:
  crontab -e
  0 23 * * * cd /path/to/yearly-data-pipeline && uv run python scripts/sync_macos.py

Requires Full Disk Access for Terminal (or whichever app runs this script):
  System Settings → Privacy & Security → Full Disk Access
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline import r2 as R2
from pipeline.config import PipelineConfig
from pipeline.r2 import make_client
from pipeline.models.bronze.macos_commands import _parse_history
from pipeline.models.bronze.macos_screentime import _query_db


def main() -> None:
    config = PipelineConfig.load()
    r2 = make_client(config)
    today = date.today().isoformat()

    commands = _parse_history()
    if commands:
        R2.upload_bytes(r2, f"bronze/inbox/macos_commands/commands_{today}.json", json.dumps(commands).encode(), "application/json")
        print(f"  {len(commands)} commands → bronze/inbox/macos_commands")
    else:
        print("  no commands found, skipping")

    sessions = _query_db()
    R2.upload_bytes(r2, f"bronze/inbox/macos_screentime/screentime_{today}.json", json.dumps(sessions).encode(), "application/json")
    print(f"  {len(sessions)} screentime records → bronze/inbox/macos_screentime")


if __name__ == "__main__":
    main()
