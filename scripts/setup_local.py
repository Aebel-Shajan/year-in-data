"""
Start MinIO and create the local bucket with the correct public-read policy.
Run this once after `make up` before using `make pipeline` or `make dev` locally.

  uv run python scripts/setup_local.py
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
import tomllib
import urllib.request
from pathlib import Path

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from dotenv import dotenv_values

ROOT = Path(__file__).parent.parent


def _load_config() -> tuple[str, str, object]:
    env_file = ROOT / ".env"
    if not env_file.exists():
        shutil.copy(ROOT / ".env.local.example", env_file)
        print("✓ Created .env from .env.local.example")

    env = dotenv_values(env_file)
    with open(ROOT / "config" / "test.toml", "rb") as f:
        toml = tomllib.load(f)

    endpoint = env.get("R2_ENDPOINT_URL") or "http://localhost:9000"
    bucket = toml["r2"]["bucket_name"]
    r2 = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=env["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=env["R2_SECRET_ACCESS_KEY"],
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )
    return endpoint, bucket, r2


def ensure_minio(endpoint: str) -> None:
    subprocess.run(["docker", "compose", "up", "-d"], check=True, cwd=ROOT)

    print("· Waiting for MinIO", end="", flush=True)
    for _ in range(20):
        try:
            urllib.request.urlopen(f"{endpoint}/minio/health/live", timeout=1)
            print(" ✓")
            return
        except Exception:
            print(".", end="", flush=True)
            time.sleep(1)

    print("\n✗ MinIO did not start. Run: docker compose logs minio")
    sys.exit(1)


def ensure_bucket(r2, bucket: str) -> None:
    try:
        r2.head_bucket(Bucket=bucket)
    except ClientError:
        r2.create_bucket(Bucket=bucket)
        print(f"✓ Created bucket '{bucket}'")

    policy = json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"AWS": "*"},
            "Action": ["s3:GetObject"],
            "Resource": [f"arn:aws:s3:::{bucket}/web/*"],
        }],
    })
    r2.put_bucket_policy(Bucket=bucket, Policy=policy)
    print(f"✓ Bucket '{bucket}' ready")


def main() -> None:
    endpoint, bucket, r2 = _load_config()
    ensure_minio(endpoint)
    ensure_bucket(r2, bucket)


if __name__ == "__main__":
    main()
