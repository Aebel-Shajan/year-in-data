"""
One-time setup for the production Cloudflare R2 buckets.

  - Creates pipeline bucket (private) and web bucket (public) if they don't exist
  - Applies CORS rules from config/cors.json to the web bucket

  uv run python scripts/setup_r2.py

Run once when setting up a new environment, and again whenever cors.json changes.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

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
    apply_cors(web_r2.client, config.web_bucket_name, cors_rules)

    print("✓ R2 setup complete")


def ensure_bucket(r2, bucket: str) -> None:
    from botocore.exceptions import ClientError

    try:
        r2.client.head_bucket(Bucket=bucket)
        print(f"· Bucket '{bucket}' found")
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code in ("404", "NoSuchBucket"):
            r2.client.create_bucket(Bucket=bucket)
            print(f"✓ Bucket '{bucket}' created")
        else:
            raise


def apply_cors(client, bucket: str, cors_rules: list) -> None:
    try:
        client.put_bucket_cors(Bucket=bucket, CORSConfiguration={"CORSRules": cors_rules})
        print(f"✓ CORS rules applied to '{bucket}'")
    except Exception as e:
        print(f"✗ Failed to apply CORS rules: {e}")


if __name__ == "__main__":
    main()
