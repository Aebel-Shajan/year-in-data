"""
Entry point for the weekly pipeline.

  uv run python -m pipeline.main
  uv run python -m pipeline.main --config config/config.toml
"""

import argparse
import os
import sys
import traceback
from pathlib import Path

from pipeline.config import Config, Secrets
from pipeline.extractors import fitbit, github, kindle, strong
from pipeline.extractors.github import _DEFAULT_API_URL
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
    args = parser.parse_args()

    secrets = Secrets()  # type: ignore[call-arg]
    config = Config.load(args.config) if args.config else Config.load()
    r2 = make_client(secrets, config)

    extractors = []
    if config.run_github:
        extractors.append(("github", lambda: github.run(r2, secrets, config, api_url=os.getenv("GITHUB_API_URL", _DEFAULT_API_URL))))
    if config.run_fitbit:
        extractors.append(("fitbit", lambda: fitbit.run(r2)))
    if config.run_kindle:
        extractors.append(("kindle", lambda: kindle.run(r2)))
    if config.run_strong:
        extractors.append(("strong", lambda: strong.run(r2)))

    failures = []
    for name, fn in extractors:
        print(f"── {name} ──────────────────────")
        try:
            fn()
        except Exception:
            traceback.print_exc()
            failures.append(name)

    if failures:
        print(f"\n✗ Failed: {', '.join(failures)}")
        sys.exit(1)
    else:
        print("\nPipeline complete.")


if __name__ == "__main__":
    main()
