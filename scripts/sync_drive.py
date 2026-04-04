"""
Download files from a public Google Drive folder and upload new ones to R2 inbox.

Drive folder structure:
  <shared folder>/
    fitbit/    ← Google Takeout zips
    kindle/    ← Amazon reading insights CSVs
    strong/    ← Strong app CSVs

Files already present in R2 are skipped. Files are never deleted from Drive —
store_partitions handles data-level deduplication across overlapping exports.

Setup:
  1. Right-click your Drive folder → Share → Anyone with the link (Viewer)
  2. Copy the share URL into .env as DRIVE_SHARE_URL
  3. uv run python scripts/sync_drive.py

  uv run python scripts/sync_drive.py
"""

from __future__ import annotations

import tempfile
import tomllib
from pathlib import Path

import boto3
import gdown
from botocore.config import Config as BotocoreConfig
from botocore.exceptions import ClientError
from dotenv import dotenv_values

ROOT = Path(__file__).parent.parent

env = dotenv_values(ROOT / ".env")
with open(ROOT / "config" / "config.toml", "rb") as f:
    _toml = tomllib.load(f)

ASSET_NAMES = ["fitbit", "kindle", "strong"]
BUCKET: str = _toml["r2"]["bucket_name"]

ENDPOINT = env.get("R2_ENDPOINT_URL") or f"https://{env['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com"
r2 = boto3.client(
    "s3",
    endpoint_url=ENDPOINT,
    aws_access_key_id=env["R2_ACCESS_KEY_ID"],
    aws_secret_access_key=env["R2_SECRET_ACCESS_KEY"],
    config=BotocoreConfig(signature_version="s3v4"),
    region_name="us-east-1",
)


def _r2_exists(key: str) -> bool:
    try:
        r2.head_object(Bucket=BUCKET, Key=key)
        return True
    except ClientError:
        return False


def main() -> None:
    share_url = env.get("DRIVE_SHARE_URL")
    if not share_url:
        raise SystemExit("Add DRIVE_SHARE_URL to .env (the public share link for your Drive folder)")

    print("── Syncing from Google Drive ────────────────────────────────────")

    with tempfile.TemporaryDirectory() as tmp:
        print("· Downloading from Drive...")
        gdown.download_folder(url=share_url, output=tmp, use_cookies=False, quiet=True)

        total = 0
        for source in ASSET_NAMES:
            source_dir = Path(tmp) / source
            if not source_dir.exists():
                print(f"  [{source}] no subfolder found, skipping")
                continue
            for file in sorted(source_dir.iterdir()):
                if not file.is_file():
                    continue
                key = f"raw/{source}/inbox/{file.name}"
                if _r2_exists(key):
                    print(f"  [{source}] already in R2: {file.name}")
                    continue
                with open(file, "rb") as f:
                    r2.put_object(Bucket=BUCKET, Key=key, Body=f)
                print(f"  [{source}] → {key}")
                total += 1

    print(f"✓ {total} new file(s) synced\n")


if __name__ == "__main__":
    main()
