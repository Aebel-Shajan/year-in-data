"""
Export daily Parquet files to the public web bucket as JSON.

Run as part of the website deploy process to publish the latest data
before the site is built.

  uv run python scripts/export_json.py
"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline import r2 as R2
from pipeline.config import PipelineConfig
from pipeline.jobs import export


def main() -> None:
    ROOT = Path(__file__).parent.parent
    config = PipelineConfig.load(ROOT / "config" / "config.toml", ".env")
    r2 = R2.make_client(config)
    web_r2 = R2.make_web_client(config)
    try:
        export.run(r2, web_r2)
    except Exception:
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
