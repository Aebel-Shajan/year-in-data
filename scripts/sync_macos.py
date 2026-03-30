"""
Sync macOS Screen Time data to R2.

Run on a cron schedule to keep your screen time heatmap up to date:

  uv run python scripts/sync_screentime.py

To run daily at 11pm via crontab:
  crontab -e
  0 23 * * * cd /path/to/yearly-data-pipeline && uv run python scripts/sync_screentime.py

Requires Full Disk Access for Terminal (or whichever app runs this script):
  System Settings → Privacy & Security → Full Disk Access
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.config import Config, Secrets
from pipeline.extractors import screentime, zsh_history
from pipeline.r2 import make_client


def main() -> None:
    secrets = Secrets()  # type: ignore[call-arg]
    config = Config.load()
    r2 = make_client(secrets, config)
    screentime.run(r2)
    zsh_history.run(r2)


if __name__ == "__main__":
    main()
