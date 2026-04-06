"""
Cloudflare R2 client and all storage operations for the pipeline.

Medallion architecture:
  bronze/inbox/{asset_name}/              ← all raw files land here
    - file-based asset_names: user uploads ZIP/CSV
    - API asset_names:   ingest() saves raw JSON response
    - local asset_names: ingest() dumps query results as JSON
  bronze/{asset_name}/{YYYY-MM-DD}/       ← archived after bronze_to_silver runs
  silver/{asset_name}/{metric}.parquet    ← cleaned, normalized, asset_name units, row-level
  gold/{asset_name}/{metric}.parquet      ← daily aggregated totals, display units
  web/{asset_name}/{metric}.json          ← public JSON consumed by the website
"""

from __future__ import annotations

import io
import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Literal

import boto3
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


# ── Key-path helpers ──────────────────────────────────────────────────────────

def silver_key(location: str) -> str:
    return f"silver/{location}.parquet"


def gold_key(location: str) -> str:
    return f"gold/{location}.parquet"


def web_key(location: str) -> str:
    return f"web/{location}.json"


def web_public_url(r2: R2Client, location: str) -> str:
    return f"{r2.public_url}/{web_key(location)}"


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
    """Download a Parquet file and return it, or None if it doesn't exist.

    Optionally filters rows by the 'date' column (inclusive on both ends).
    """
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
    """Write df to a Parquet file on R2.

    By default merges with any existing file, deduplicating to preserve history.
    Pass overwrite=True to replace entirely — used for silver and gold layers
    which are always fully recomputed from the previous layer.
    """
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


# ── Web JSON export ───────────────────────────────────────────────────────────

def export_daily_aggregated_json(
    r2: R2Client,
    web_r2: R2Client,
    output_key: str,
    unit: str,
    label: str,
) -> None:
    """Read a gold Parquet from r2 and write aggregated JSON to web_r2.

    output_key is the full gold key, e.g. "gold/fitbit/daily_calories.parquet".
    JSON is written to web_r2 as "{layer}/{metric}.json",
    e.g. "fitbit/daily_calories.json".

    Output format:
    {
      "asset_name": "fitbit", "metric": "daily_calories", "unit": "kcal",
      "label": "Calories burned", "updated_at": "2025-01-20",
      "data": [{"date": "2025-01-01", "value": 2100.0}, ...]
    }
    """
    if not exists(r2, output_key):
        return

    _, layer, filename = output_key.split("/")
    metric = filename.removesuffix(".parquet")
    web_key_path = f"{layer}/{metric}.json"

    full = pl.read_parquet(io.BytesIO(download_bytes(r2, output_key))).sort("date")

    records: list[dict] = []
    for row in full.iter_rows(named=True):
        entry: dict = {"date": str(row["date"]), "value": row["value"]}
        if row.get("category") is not None:
            entry["category"] = row["category"]
        if row.get("image_url") is not None:
            entry["image_url"] = row["image_url"]
        records.append(entry)

    payload = {
        "asset_name": layer,
        "metric": metric,
        "unit": unit,
        "label": label,
        "updated_at": str(date.today()),
        "data": records,
    }
    upload_bytes(web_r2, web_key_path, json.dumps(payload).encode(), "application/json")


# ── Bronze inbox archival ─────────────────────────────────────────────────────

def archive_inbox(r2: R2Client, inbox_key: str, archive_prefix: str) -> None:
    """Move all files from inbox_key/ to archive_prefix/{date}/{filename}.

    inbox_key: e.g. "bronze/inbox/fitbit"
    archive_prefix: e.g. "bronze/fitbit"
    """
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


def list_bronze_keys(
    r2: R2Client,
    bronze_prefix: str,
    start: date | None = None,
    end: date | None = None,
) -> list[str]:
    """List archived bronze files under bronze_prefix.

    bronze_prefix: e.g. "bronze/fitbit" (no trailing slash)
    Keys follow the pattern: {bronze_prefix}/{YYYY-MM-DD}/{filename}
    start/end filter on the archive folder date (when the file was archived).
    """
    all_keys = list_keys(r2, bronze_prefix + "/")
    if not start and not end:
        return all_keys

    filtered = []
    for key in all_keys:
        parts = key.split("/")
        if len(parts) < 4:
            continue
        try:
            folder_date = date.fromisoformat(parts[2])
        except ValueError:
            continue
        if start and folder_date < start:
            continue
        if end and folder_date > end:
            continue
        filtered.append(key)
    return filtered
