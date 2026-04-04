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

import argparse
import sys
from datetime import date
from pathlib import Path

from pipeline import stages  # type: ignore[attr-defined]
from pipeline.config import Config, Secrets
from pipeline.r2 import make_client


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the yearly data pipeline.")
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        metavar="PATH",
        help="Path to config.toml (default: config/config.toml)",
    )
    parser.add_argument(
        "--stage",
        choices=["bronze", "silver", "gold", "all"],
        default="all",
        help="Which stage to run (default: all)",
    )
    parser.add_argument(
        "--start",
        type=date.fromisoformat,
        default=None,
        metavar="YYYY-MM-DD",
        help="Filter gold models to dates on or after this date",
    )
    parser.add_argument(
        "--end",
        type=date.fromisoformat,
        default=None,
        metavar="YYYY-MM-DD",
        help="Filter gold models to dates on or before this date",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print gold model output without writing to R2",
    )
    args = parser.parse_args()

    secrets = Secrets()  # type: ignore[call-arg]
    config = Config.load(args.config) if args.config else Config.load()
    r2 = make_client(secrets, config)

    failures: list[str] = []

    if args.stage in ("bronze", "all"):
        failures += stages.run_bronze(r2, secrets, config)
    if args.stage in ("silver", "all"):
        failures += stages.run_silver(r2)
    if args.stage in ("gold", "all"):
        failures += stages.run_gold(r2, start=args.start, end=args.end, dry_run=args.dry_run)

    if failures:
        print(f"\n✗ Failed: {', '.join(failures)}")
        sys.exit(1)
    else:
        print("\nDone.")


if __name__ == "__main__":
    main()
