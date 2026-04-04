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

import httpx

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
    if config.runtime_env != "local":
        enable_public_access(config.endpoint_url, config.web_bucket_name, config.secrets.cloudflare_api_token)
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


def enable_public_access(endpoint_url: str, bucket: str, api_token: str) -> None:
    """Enable the pub-*.r2.dev development URL on a bucket via the Cloudflare REST API."""
    account_id = endpoint_url.removeprefix("https://").split(".")[0]
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/r2/buckets/{bucket}/policy"
    resp = httpx.put(
        url,
        headers={"Authorization": f"Bearer {api_token}"},
        json={"allowed_public_access": True},
    )
    if resp.status_code == 200:
        dev_url = resp.json().get("result", {}).get("development_url", "")
        print(f"✓ Public access enabled on '{bucket}'")
        if dev_url:
            print(f"  URL: {dev_url}")
            print(f"  Update web_public_url in config/config.toml if needed")
    else:
        print(f"✗ Failed to enable public access: {resp.status_code} {resp.text}")


def apply_cors(client, bucket: str, cors_rules: list) -> None:
    try:
        client.put_bucket_cors(Bucket=bucket, CORSConfiguration={"CORSRules": cors_rules})
        print(f"✓ CORS rules applied to '{bucket}'")
    except Exception as e:
        print(f"✗ Failed to apply CORS rules: {e}")


if __name__ == "__main__":
    main()
