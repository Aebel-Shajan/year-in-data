"""
Cloudflare R2 client and all storage operations for the pipeline.

Medallion architecture:
  bronze/{source}/{metric}.parquet    ← raw source records, source schema
  silver/{source}/{metric}.parquet    ← normalized (date, category?, value in source units)
  gold/{source}/{metric}.parquet      ← daily aggregated totals, display units
  web/{source}/{metric}.json          ← public JSON consumed by the website

Raw file storage:
  raw/{source}/inbox/{filename}       ← user uploads here
  raw/{source}/{YYYY-WXX}/{filename}  ← archived after processing
"""

from __future__ import annotations

import io
import json
from dataclasses import dataclass
from datetime import date
from typing import Literal

import boto3
import polars as pl
from botocore.config import Config as BotocoreConfig
from botocore.exceptions import ClientError

from pipeline.config import Config, Secrets


@dataclass
class R2Client:
    client: object  # boto3 S3 client
    bucket: str
    public_url: str


def make_client(secrets: Secrets, config: Config) -> R2Client:
    endpoint = (
        secrets.r2_endpoint_url
        or f"https://{secrets.r2_account_id}.r2.cloudflarestorage.com"
    )
    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=secrets.r2_access_key_id,
        aws_secret_access_key=secrets.r2_secret_access_key,
        config=BotocoreConfig(signature_version="s3v4"),
        region_name="auto",
    )
    return R2Client(
        client=client,
        bucket=config.r2_bucket_name,
        public_url=config.r2_public_url.rstrip("/"),
    )


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

def year_week(d: date | None = None) -> str:
    """ISO year-week string, e.g. '2025-W12'. Used for raw archive keys."""
    iso = (d or date.today()).isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def inbox_prefix(source: str) -> str:
    return f"bronze/inbox/{source}"


def archive_key(source: str, iso_date: str, filename: str) -> str:
    return f"bronze/{source}/{iso_date}/{filename}"


def silver_key(source: str, metric: str) -> str:
    return f"silver/{source}/{metric}.parquet"


def gold_key(source: str, metric: str) -> str:
    return f"gold/{source}/{metric}.parquet"


def web_key(source: str, metric: str) -> str:
    return f"web/{source}/{metric}.json"


def web_public_url(r2: R2Client, source: str, metric: str) -> str:
    return f"{r2.public_url}/{web_key(source, metric)}"


# ── Medallion storage ─────────────────────────────────────────────────────────

def store_parquet(
        r2: R2Client, 
        key: str, 
        df: pl.DataFrame,
        sort_col: str,
        dedup_cols: list[str] | None = None,
        keep: Literal["last", "any", "none", "first"] = "last",
) -> None:
    """Merge df into an existing Parquet file, deduplicating and preserving existing rows."""
    if exists(r2, key):
        existing = pl.read_parquet(io.BytesIO(download_bytes(r2, key)))
        if dedup_cols:
            df = (
                pl.concat([df, existing])
                .unique(subset=dedup_cols, keep=keep)
                .sort("date")
            )
        else:
            df = pl.concat([df, existing]).unique(keep=keep).sort(sort_col)
    else:
        df = df.sort(sort_col)

    buf = io.BytesIO()
    df.write_parquet(buf)
    upload_bytes(r2, key, buf.getvalue())

# ── Web JSON write ────────────────────────────────────────────────────────────

def export_daily_aggregated_json(r2: R2Client, source: str, metric: str, unit: str, label: str) -> None:
    """
    Read the gold Parquet file and write aggregated JSON to web/.

    Output format:
    {
      "source": "fitbit", "metric": "calories", "unit": "kcal",
      "label": "Calories burned", "updated_at": "2025-01-20",
      "data": [{"date": "2025-01-01", "value": 2100.0}, ...]
    }
    """
    key = gold_key(source, metric)
    if not exists(r2, key):
        return

    full = pl.read_parquet(io.BytesIO(download_bytes(r2, key))).sort("date")

    records: list[dict] = []
    for row in full.iter_rows(named=True):
        entry: dict = {"date": str(row["date"]), "value": row["value"]}
        if row.get("category") is not None:
            entry["category"] = row["category"]
        if row.get("image_url") is not None:
            entry["image_url"] = row["image_url"]
        records.append(entry)

    payload = {
        "source": source,
        "metric": metric,
        "unit": unit,
        "label": label,
        "updated_at": str(date.today()),
        "data": records,
    }
    upload_bytes(r2, web_key(source, metric), json.dumps(payload).encode(), "application/json")


# ── Raw inbox archival ────────────────────────────────────────────────────────

def archive_inbox(r2: R2Client, source: str) -> None:
    iso_date = date.today().isoformat()
    for key in list_keys(r2, inbox_prefix(source)):
        filename = key.rsplit("/", 1)[-1]
        dst = archive_key(source, iso_date, filename)
        move(r2, key, dst)
        print(f"  archived {filename} → {dst}")
