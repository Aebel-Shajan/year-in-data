"""
Cloudflare R2 client and all storage operations for the pipeline.

R2 key conventions:
  raw/{source}/inbox/{filename}          ← user uploads here
  raw/{source}/{YYYY-WXX}/{filename}     ← archived after processing
  processed/{source}/{metric}/{YYYY-WXX}.parquet  ← weekly Polars partitions
  web/{source}/{metric}.json             ← public JSON consumed by the website
"""

from __future__ import annotations

import io
import json
from dataclasses import dataclass
from datetime import date

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
    """ISO year-week string, e.g. '2025-W12'."""
    iso = (d or date.today()).isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def inbox_prefix(source: str) -> str:
    return f"raw/{source}/inbox/"


def archive_key(source: str, yw: str, filename: str) -> str:
    return f"raw/{source}/{yw}/{filename}"


def processed_key(source: str, metric: str, yw: str) -> str:
    return f"processed/{source}/{metric}/{yw}.parquet"


def processed_prefix(source: str, metric: str) -> str:
    return f"processed/{source}/{metric}/"


def web_key(source: str, metric: str) -> str:
    return f"web/{source}/{metric}.json"


def web_public_url(r2: R2Client, source: str, metric: str) -> str:
    return f"{r2.public_url}/{web_key(source, metric)}"


# ── Data-lake write ───────────────────────────────────────────────────────────

def store_partitions(r2: R2Client, source: str, metric: str, df: pl.DataFrame) -> None:
    """
    Merge df into weekly Parquet partitions on R2.

    df must have columns: date (pl.Date), value (pl.Float64), and optionally
    category (pl.Utf8) and image_url (pl.Utf8).
    """
    if df.is_empty():
        return

    augmented = df.with_columns(
        pl.col("date")
        .map_elements(
            lambda d: f"{d.isocalendar()[0]}-W{d.isocalendar()[1]:02d}",
            return_dtype=pl.Utf8,
        )
        .alias("_yw")
    )

    dedup_cols = ["date"] + (["category"] if "category" in df.columns else [])

    for (yw,), week_df in augmented.group_by("_yw"):
        week_df = week_df.drop("_yw")
        key = processed_key(source, metric, yw)

        if exists(r2, key):
            existing = pl.read_parquet(io.BytesIO(download_bytes(r2, key)))
            week_df = (
                pl.concat([existing, week_df])
                .unique(subset=dedup_cols, keep="last")
                .sort("date")
            )
        else:
            week_df = week_df.sort("date")

        buf = io.BytesIO()
        week_df.write_parquet(buf)
        upload_bytes(r2, key, buf.getvalue())


# ── Web JSON write ────────────────────────────────────────────────────────────

def write_web_json(
    r2: R2Client,
    source: str,
    metric: str,
    unit: str,
    label: str,
) -> None:
    """
    Concatenate all weekly partitions and write aggregated JSON to web/.

    Output format:
    {
      "source": "fitbit", "metric": "calories", "unit": "kcal",
      "label": "Calories burned", "updated_at": "2025-01-20",
      "data": [{"date": "2025-01-01", "value": 2100.0}, ...]
    }
    """
    keys = sorted(list_keys(r2, processed_prefix(source, metric)))
    if not keys:
        return

    frames = [pl.read_parquet(io.BytesIO(download_bytes(r2, k))) for k in keys]
    full = pl.concat(frames).sort("date")

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
    yw = year_week()
    for key in list_keys(r2, inbox_prefix(source)):
        filename = key.rsplit("/", 1)[-1]
        dst = archive_key(source, yw, filename)
        move(r2, key, dst)
        print(f"  archived {filename} → {dst}")
