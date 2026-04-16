"""
Cloudflare R2 client and all storage operations for the pipeline.
"""

from __future__ import annotations

import io
import shutil
import subprocess
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Literal
from urllib.parse import urlparse
from pipeline import paths
import boto3
import httpx
import polars as pl
from botocore.config import Config as BotocoreConfig
from botocore.exceptions import ClientError

from pipeline.config import PipelineConfig


@dataclass
class R2Client:
    client: object  # boto3 S3 client
    bucket: str
    public_url: str


def _boto_client(config: PipelineConfig):
    return boto3.client(
        "s3",
        endpoint_url=config.endpoint_url,
        aws_access_key_id=config.secrets.r2_access_key_id,
        aws_secret_access_key=config.secrets.r2_secret_access_key,
        config=BotocoreConfig(signature_version="s3v4"),
        region_name="auto",
    )


def make_client(config: PipelineConfig) -> R2Client:
    return R2Client(client=_boto_client(config), bucket=config.r2_bucket_name, public_url="")


def make_web_client(config: PipelineConfig) -> R2Client:
    return R2Client(client=_boto_client(config), bucket=config.web_bucket_name, public_url="")


# ── Low-level helpers ─────────────────────────────────────────────────────────

def exists(r2: R2Client, key: str) -> bool:
    try:
        r2.client.head_object(Bucket=r2.bucket, Key=key)  # type: ignore[attr-defined]
        return True
    except ClientError:
        return False


def list_keys(r2: R2Client, prefix: str) -> list[str]:
    keys: list[str] = []
    paginator = r2.client.get_paginator("list_objects_v2")  # type: ignore[attr-defined]
    for page in paginator.paginate(Bucket=r2.bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            keys.append(obj["Key"])
    return keys


def download_bytes(r2: R2Client, key: str) -> bytes:
    resp = r2.client.get_object(Bucket=r2.bucket, Key=key)  # type: ignore[attr-defined]
    return resp["Body"].read()


def upload_bytes(r2: R2Client, key: str, data: bytes, content_type: str = "application/octet-stream") -> None:
    r2.client.put_object(Bucket=r2.bucket, Key=key, Body=data, ContentType=content_type)  # type: ignore[attr-defined]


def move(r2: R2Client, src: str, dst: str) -> None:
    """Copy then delete (R2 has no atomic rename)."""
    r2.client.copy_object(  # type: ignore[attr-defined]
        Bucket=r2.bucket,
        CopySource={"Bucket": r2.bucket, "Key": src},
        Key=dst,
    )
    r2.client.delete_object(Bucket=r2.bucket, Key=src)  # type: ignore[attr-defined]


# ── Inbox / archive helpers ───────────────────────────────────────────────────

def create_inboxes(r2) -> None:
    """Create placeholder objects for each source inbox folder."""
    sources = [
        "fitbit",
        "github",
        "gymgroup",
        "kindle",
        "macos_commands",
        "macos_screentime",
        "strong"
    ]
    for src in sources:
        placeholder = paths.inbox(src + "/.keep")
        if not exists(r2, placeholder):
            upload_bytes(r2, placeholder, b"", "application/octet-stream")
            print(f"  created {src}/")


def flush_inbox(r2: R2Client, tag: str, inbox_key: str, archive_key: str) -> None:
    """Move any inbox files to the archive."""
    keys = list_keys(r2, inbox_key + "/")
    if not keys:
        return
    archive_inbox(r2, inbox_key, archive_key)
    print(f"[{tag}] archived {len(keys)} file(s)")


def get_archive_keys(
    r2: R2Client,
    archive_key: str,
    parquet_key: str,
    extension: str,
    start: date | None = None,
    end: date | None = None,
) -> list[str]:
    """Return archived files to process, filtered by extension and date range.

    start defaults to the latest date in parquet_key (for incremental processing).
    extension should include the dot, e.g. ".zip", ".json", ".csv".
    """
    if start is None:
        start = latest_date(r2, parquet_key)
    return [
        k for k in list_archive_keys(r2, archive_key, start=start, end=end)
        if k.lower().endswith(extension)
    ]


def archive_inbox(r2: R2Client, inbox_key: str, archive_prefix: str) -> None:
    """Move all files from inbox_key/ to archive_prefix/{date}/{filename}."""
    now = datetime.now(tz=timezone.utc)
    iso_date = now.date().isoformat()
    timestamp = now.strftime("%Y-%m-%d_%H%M%S")
    for key in list_keys(r2, inbox_key + "/"):
        if key.endswith("/.keep"):
            continue
        ext = key.rsplit(".", 1)[-1] if "." in key else ""
        filename = f"{archive_prefix.split('/')[-1]}_{timestamp}.{ext}"
        dst = f"{archive_prefix}/{iso_date}/{filename}"
        move(r2, key, dst)
        print(f"  archived → {dst}")


def list_archive_keys(
    r2: R2Client,
    archive_prefix: str,
    start: date | None = None,
    end: date | None = None,
) -> list[str]:
    """List archived files under archive_prefix, optionally filtered by date range.

    Keys follow the pattern: {archive_prefix}/{YYYY-MM-DD}/{filename}
    start/end filter on the folder date (i.e. when the file was archived).
    """
    all_keys = list_keys(r2, archive_prefix + "/")
    if not start and not end:
        return all_keys

    filtered = []
    for key in all_keys:
        parts = key.split("/")
        if len(parts) < 3:
            continue
        try:
            folder_date = date.fromisoformat(parts[-2])
        except ValueError:
            continue
        if start and folder_date < start:
            continue
        if end and folder_date > end:
            continue
        filtered.append(key)
    return filtered


# ── Parquet helpers ───────────────────────────────────────────────────────────

def latest_date(r2: R2Client, key: str) -> date | None:
    """Return max(date) - 1 day from a Parquet file, or None if it doesn't exist."""
    if not exists(r2, key):
        return None
    df = pl.read_parquet(io.BytesIO(download_bytes(r2, key)))
    if df.is_empty() or "date" not in df.columns:
        return None
    max_val = df["date"].max()
    if max_val is None:
        return None
    return date.fromisoformat(str(max_val)) - timedelta(days=1)


def load_parquet(
    r2: R2Client,
    key: str,
    start: date | None = None,
    end: date | None = None,
) -> pl.DataFrame | None:
    """Download a Parquet file and return it filtered by date, or None if it doesn't exist."""
    if not exists(r2, key):
        return None
    df = pl.read_parquet(io.BytesIO(download_bytes(r2, key)))
    if start:
        df = df.filter(pl.col("date") >= start)
    if end:
        df = df.filter(pl.col("date") <= end)
    return df


def store_parquet(
    r2: R2Client,
    key: str,
    df: pl.DataFrame,
    sort_col: str,
    dedup_cols: list[str] | None = None,
    keep: Literal["last", "first", "any", "none"] = "last",
    overwrite: bool = False,
) -> None:
    """Write df to a Parquet file on R2, merging with any existing data by default."""
    if not overwrite and exists(r2, key):
        existing = pl.read_parquet(io.BytesIO(download_bytes(r2, key)))
        if dedup_cols:
            df = (
                pl.concat([df, existing])
                .unique(subset=dedup_cols, keep=keep)
                .sort(sort_col)
            )
        else:
            df = pl.concat([df, existing]).unique(keep=keep).sort(sort_col)
    else:
        df = df.sort(sort_col)

    buf = io.BytesIO()
    df.write_parquet(buf)
    upload_bytes(r2, key, buf.getvalue())


# ── Bucket setup helpers ──────────────────────────────────────────────────────

def enable_r2_dev_public(endpoint_url: str, bucket: str, api_token: str) -> None:
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


def apply_cors(client, bucket: str, cors_rules: list) -> None:
    try:
        client.put_bucket_cors(Bucket=bucket, CORSConfiguration={"CORSRules": cors_rules})
        print(f"✓ CORS rules applied to '{bucket}'")
    except Exception as e:
        print(f"✗ Failed to apply CORS rules: {e}")

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
