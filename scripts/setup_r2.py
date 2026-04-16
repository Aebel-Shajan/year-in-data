"""
One-time setup for the production Cloudflare R2 buckets.

  - Creates pipeline bucket (private) and web bucket (public) if they don't exist
  - Enables public development URL (pub-*.r2.dev) on the web bucket
  - Applies CORS rules from config/cors.json to the web bucket

  uv run python scripts/setup_r2.py

Run once when setting up a new environment, and again whenever cors.json changes.

Requires a Cloudflare API token with R2 edit permission:
  dash.cloudflare.com → My Profile → API Tokens → Create Token → R2:Edit
  Add it to .env as CLOUDFLARE_API_TOKEN
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from pipeline.bucket_setup import apply_cors, create_inboxes, enable_r2_dev_public, ensure_bucket
from pipeline.config import PipelineConfig
from pipeline.r2 import make_client, make_web_client


def main() -> None:
    config = PipelineConfig.load()
    r2 = make_client(config)
    web_r2 = make_web_client(config)

    with open(ROOT / "config" / "cors.json") as f:
        cors_rules = json.load(f)

    ensure_bucket(r2, config.r2_bucket_name)
    ensure_bucket(web_r2, config.web_bucket_name)
    enable_r2_dev_public(config.endpoint_url, config.web_bucket_name, config.secrets.cloudflare_api_token)
    apply_cors(web_r2, cors_rules)
    create_inboxes(r2)
    print("✓ R2 setup complete")




if __name__ == "__main__":
    main()
