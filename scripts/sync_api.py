"""
Fetch data from external APIs and upload to the R2 inbox.

Covers all API-based sources:
  - GitHub contributions (GraphQL API)
  - Gym Group check-ins (HTTP API)
  - Garmin Connect wellness + activities

Does not archive — run the main pipeline afterwards to process the inbox.

  uv run python scripts/sync_api.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.common.config import PipelineConfig
from pipeline.common.r2 import make_client
from pipeline.extract import garmin, github, gymgroup


def main() -> None:
    config = PipelineConfig.load()
    r2 = make_client(config)
    failures: list[str] = []

    try:
        github.fetch(r2, config)
    except Exception as e:
        print(f"  ✗ github: {e}", file=sys.stderr)
        failures.append("github")

    try:
        gymgroup.fetch(r2, config)
    except Exception as e:
        print(f"  ✗ gymgroup: {e}", file=sys.stderr)
        failures.append("gymgroup")

    try:
        garmin.fetch(r2, config)
    except Exception as e:
        print(f"  ✗ garmin: {e}", file=sys.stderr)
        failures.append("garmin")

    if failures:
        print(f"\n✗ Failed: {', '.join(failures)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
