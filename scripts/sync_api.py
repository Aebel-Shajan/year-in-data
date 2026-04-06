"""
Fetch data from external APIs and upload to the R2 bronze inbox.

Covers all API-based bronze sources:
  - GitHub contributions (GraphQL API)
  - Gym Group check-ins (HTTP API)

Does not archive — run the main pipeline afterwards to process the inbox.

  uv run python scripts/sync_api.py
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
from pipeline.models.bronze.github_api_response import _fetch as _fetch_github
from pipeline.models.bronze.gymgroup_api import _fetch as _fetch_gymgroup
from pipeline.stages import BRONZE_MODELS


def _inbox(tag: str) -> str:
    return next(m.input_key for m in BRONZE_MODELS if m.tag == tag)


def main() -> None:
    config = PipelineConfig.load()
    r2 = make_client(config)
    today = date.today().isoformat()
    failures: list[str] = []

    # GitHub
    try:
        days = _fetch_github(config)
        if days:
            key = f"{_inbox('github')}/contributions_{today}.json"
            R2.upload_bytes(r2, key, json.dumps(days).encode(), "application/json")
            print(f"  {len(days)} contribution days → {_inbox('github')}")
        else:
            print("  github: no contributions found")
    except Exception as e:
        print(f"  ✗ github: {e}", file=sys.stderr)
        failures.append("github")

    # Gym Group
    try:
        check_ins = _fetch_gymgroup(config.secrets.gym_group_username, config.secrets.gym_group_password)
        if check_ins:
            key = f"{_inbox('gymgroup')}/checkins_{today}.json"
            R2.upload_bytes(r2, key, json.dumps(check_ins).encode(), "application/json")
            print(f"  {len(check_ins)} check-ins → {_inbox('gymgroup')}")
        else:
            print("  gymgroup: no check-ins found")
    except Exception as e:
        print(f"  ✗ gymgroup: {e}", file=sys.stderr)
        failures.append("gymgroup")

    if failures:
        print(f"\n✗ Failed: {', '.join(failures)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
