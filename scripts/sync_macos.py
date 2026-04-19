"""
Sync macOS Screen Time and shell history to the R2 inbox.

Uploads today's data to the inbox so the main pipeline can later archive
and process it. Does not archive or run aggregation.

Run on a cron schedule to keep the inbox fresh:

  uv run python scripts/sync_macos.py

To run daily at 11pm via crontab:
  crontab -e
  0 23 * * * cd /path/to/yearly-data-pipeline && uv run python scripts/sync_macos.py

Requires Full Disk Access for Terminal (or whichever app runs this script):
  System Settings → Privacy & Security → Full Disk Access
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.common.config import PipelineConfig
from pipeline.common.r2 import make_client
from pipeline.jobs import macos_commands, macos_screentime


def main() -> None:
    config = PipelineConfig.load()
    r2 = make_client(config)

    macos_commands.fetch(r2, config)
    macos_screentime.fetch(r2, config)


if __name__ == "__main__":
    main()
