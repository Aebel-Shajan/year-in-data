"""
One-time bucket setup operations for both local MinIO and production R2.
Not used by the pipeline at runtime.
"""

from __future__ import annotations

import shutil
import subprocess
from urllib.parse import urlparse

import httpx
from botocore.exceptions import ClientError

from pipeline.common import paths
from pipeline.common.r2 import R2Client, exists, upload_bytes


def ensure_bucket(r2: R2Client, bucket: str) -> None:
    try:
        r2.client.head_bucket(Bucket=bucket)  # type: ignore[attr-defined]
        print(f"· Bucket '{bucket}' found")
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code in ("404", "NoSuchBucket"):
            r2.client.create_bucket(Bucket=bucket)  # type: ignore[attr-defined]
            print(f"✓ Bucket '{bucket}' created")
        else:
            raise


def create_inboxes(r2: R2Client) -> None:
    """Create placeholder objects for each source inbox folder."""
    sources = [
        "fitbit", "github", "gymgroup", "kindle",
        "macos_commands", "macos_screentime", "strong",
    ]
    for src in sources:
        placeholder = paths.construct_inbox_path(src + "/.keep")
        if not exists(r2, placeholder):
            upload_bytes(r2, placeholder, b"", "application/octet-stream")
            print(f"  created {src}/")


def apply_cors(r2: R2Client, cors_rules: list) -> None:
    try:
        r2.client.put_bucket_cors(  # type: ignore[attr-defined]
            Bucket=r2.bucket, CORSConfiguration={"CORSRules": cors_rules}
        )
        print(f"✓ CORS rules applied to '{r2.bucket}'")
    except Exception as e:
        print(f"✗ Failed to apply CORS rules: {e}")


def enable_r2_dev_public(endpoint_url: str, bucket: str, api_token: str) -> None:
    host = urlparse(endpoint_url).hostname or ""
    account_id = host.split(".")[0]
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/r2/buckets/{bucket}/domains/managed"

    resp = httpx.put(
        url,
        headers={"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"},
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
            print("⚠️ Public access wasn't enabled for some reason")
    else:
        print(f"✗ Failed to enable public access: {resp.status_code} {data}")


def set_public_policy(endpoint_url: str, bucket: str) -> None:
    """Grant anonymous read access to all objects via mc CLI (MinIO local dev only)."""
    if not shutil.which("mc"):
        print("✗ 'mc' not found — install MinIO Client and run manually:")
        print(f"    mc alias set myminio {endpoint_url} minioadmin minioadmin")
        print(f"    mc anonymous set public myminio/{bucket}")
        return

    alias = "setup-r2-local"
    try:
        subprocess.run(
            ["mc", "alias", "set", alias, endpoint_url, "minioadmin", "minioadmin"],
            check=True, capture_output=True,
        )
        subprocess.run(
            ["mc", "anonymous", "set", "public", f"{alias}/{bucket}"],
            check=True, capture_output=True,
        )
        print(f"✓ Public read policy applied to '{bucket}'")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to set public policy: {e.stderr.decode().strip()}")
