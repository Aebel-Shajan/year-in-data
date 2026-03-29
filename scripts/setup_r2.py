"""
One-time setup for the production Cloudflare R2 bucket.

  - Creates the bucket if it doesn't exist
  - Applies a public-read policy on web/* (serves JSON to the website)
  - Applies CORS rules from config/cors.json

  uv run python scripts/setup_r2.py

Run once when setting up a new environment, and again whenever cors.json changes.
"""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from dotenv import dotenv_values

ROOT = Path(__file__).parent.parent

env = dotenv_values(ROOT / ".env")
with open(ROOT / "config" / "config.toml", "rb") as f:
    toml = tomllib.load(f)
with open(ROOT / "config" / "cors.json") as f:
    cors_rules = json.load(f)

endpoint = env.get("R2_ENDPOINT_URL") or f"https://{env['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com"
bucket = toml["r2"]["bucket_name"]

client = boto3.client(
    "s3",
    endpoint_url=endpoint,
    aws_access_key_id=env["R2_ACCESS_KEY_ID"],
    aws_secret_access_key=env["R2_SECRET_ACCESS_KEY"],
    config=Config(signature_version="s3v4"),
    region_name="auto",
)


def ensure_bucket() -> None:
    try:
        client.head_bucket(Bucket=bucket)
        print(f"· Bucket '{bucket}' already exists")
    except ClientError:
        client.create_bucket(Bucket=bucket)
        print(f"✓ Created bucket '{bucket}'")


def apply_policy() -> None:
    policy = json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"AWS": "*"},
            "Action": ["s3:GetObject"],
            "Resource": [f"arn:aws:s3:::{bucket}/web/*"],
        }],
    })
    client.put_bucket_policy(Bucket=bucket, Policy=policy)
    print(f"✓ Public-read policy applied to '{bucket}/web/*'")


def apply_cors() -> None:
    client.put_bucket_cors(
        Bucket=bucket,
        CORSConfiguration={"CORSRules": cors_rules},
    )
    origins = [o for rule in cors_rules for o in rule["AllowedOrigins"]]
    print(f"✓ CORS applied — allowed origins: {origins}")


if __name__ == "__main__":
    ensure_bucket()
    apply_policy()
    apply_cors()
    print(f"\nBucket '{bucket}' is ready.")
