"""
Entry point for the yearly data pipeline.

  uv run python -m pipeline.main                          # run all stages
  uv run python -m pipeline.main --stage ingest           # fetch raw data only
  uv run python -m pipeline.main --stage silver           # build silver tables
  uv run python -m pipeline.main --stage gold             # build gold tables
  uv run python -m pipeline.main --stage gold --dry-run   # preview without writing
  uv run python -m pipeline.main --stage gold --start 2025-01-01 --end 2025-03-31
"""

from __future__ import annotations

import sys
from pathlib import Path

from pipeline import stages  # type: ignore[attr-defined]
from pipeline.config import PipelineConfig
from pipeline.r2 import make_client


def run_pipeline(
        config_path: Path | None = None,
        env_path: str | None = None
):
    config = PipelineConfig.load()
    if config_path and env_path:
        config = PipelineConfig.load(config_path, env_path)

    r2 = make_client(config)

    failures: list[str] = []
    failures += stages.run_bronze(r2, config)
    failures += stages.run_silver(r2, config)
    failures += stages.run_gold(r2, config)

    if failures:
        print(f"\n✗ Failed: {', '.join(failures)}")
        sys.exit(1)
    else:
        print("\nDone.")

if __name__ == "__main__":
    run_pipeline()
