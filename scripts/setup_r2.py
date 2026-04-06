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
from pipeline.r2 import make_client, make_web_client, upload_bytes
from pipeline.stages import BRONZE_MODELS


def main() -> None:
    config = PipelineConfig.load()
    r2 = make_client(config)
    web_r2 = make_web_client(config)

    with open(ROOT / "config" / "cors.json") as f:
        cors_rules = json.load(f)

    ensure_bucket(r2, config.r2_bucket_name)
    ensure_bucket(web_r2, config.web_bucket_name)
    if config.runtime_env != "local":
        enable_r2_dev_public(config.endpoint_url, config.web_bucket_name, config.secrets.cloudflare_api_token)
    apply_cors(web_r2.client, config.web_bucket_name, cors_rules)
    create_inboxes(r2)

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


import httpx
from urllib.parse import urlparse

def enable_r2_dev_public(endpoint_url: str, bucket: str, api_token: str) -> None:
    # extract account ID from the endpoint hostname
    host = urlparse(endpoint_url).hostname or ""
    account_id = host.split(".")[0]

    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/r2/buckets/{bucket}/domains/managed"

    resp = httpx.put(
        url,
        headers={
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        },
        json={"enabled": True},
        timeout=30.0,
    )
    data = resp.json()
    if resp.status_code == 200 and data.get("success"):
        enabled = data["result"]["enabled"]
        domain = data["result"]["domain"]
        if enabled:
            print(f"✓ Public r2.dev enabled: https://{domain}")
        else:
            print(f"⚠️ Public access wasn’t enabled for some reason")
    else:
        print(f"✗ Failed to enable public access: {resp.status_code} {data}")

def create_inboxes(r2) -> None:
    """Create placeholder objects for each bronze inbox folder."""
    from pipeline.r2 import exists
    for model in BRONZE_MODELS:
        placeholder = model.input_key + "/.keep"
        if not exists(r2, placeholder):
            upload_bytes(r2, placeholder, b"", "application/octet-stream")
            print(f"  created {model.input_key}/")


def apply_cors(client, bucket: str, cors_rules: list) -> None:
    try:
        client.put_bucket_cors(Bucket=bucket, CORSConfiguration={"CORSRules": cors_rules})
        print(f"✓ CORS rules applied to '{bucket}'")
    except Exception as e:
        print(f"✗ Failed to apply CORS rules: {e}")


if __name__ == "__main__":
    main()
