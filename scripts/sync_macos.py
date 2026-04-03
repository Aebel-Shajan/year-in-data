"""
Sync macOS Screen Time and shell history to R2.

Run on a cron schedule to keep the bronze inbox fresh:

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

from pipeline import stages
from pipeline.config import Config, Secrets
from pipeline.r2 import make_client


def main() -> None:
    secrets = Secrets()  # type: ignore[call-arg]
    config = Config.load()
    r2 = make_client(secrets, config)

    failures: list[str] = []
    failures += stages.run_bronze(r2, secrets, config)
    failures += stages.run_silver(r2, config)
    failures += stages.run_gold(r2)

    if failures:
        print(f"\n✗ Failed: {', '.join(failures)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
