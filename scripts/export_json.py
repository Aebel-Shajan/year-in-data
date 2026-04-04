"""
Export gold-layer Parquet files to web-facing JSON in R2.

Run as part of the website deploy process to publish the latest gold data
before the site is built.

  uv run python scripts/export_json.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline import r2 as R2
from pipeline.config import Config, Secrets
from pipeline.r2 import make_client
from pipeline.stages import GOLD_MODELS


def main() -> None:
    secrets = Secrets()  # type: ignore[call-arg]
    config = Config.load()
    r2 = make_client(secrets, config)

    for model in GOLD_MODELS:
        R2.export_daily_aggregated_json(r2, model.output_key, model.unit, model.label)
        _, layer, filename = model.output_key.split("/")
        print(f"  exported web/{layer}/{filename.removesuffix('.parquet')}.json")


if __name__ == "__main__":
    main()
