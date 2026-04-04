"""
Start MinIO and create the local bucket with the correct public-read policy.
Run this once after `make up` before using `make pipeline` or `make dev` locally.

  uv run python scripts/setup_local.py
"""

from __future__ import annotations

import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from botocore.exceptions import ClientError

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from pipeline.config import PipelineConfig
import pipeline.r2 as R2


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
        r2.client.head_bucket(Bucket=bucket)
    except ClientError:
        r2.client.create_bucket(Bucket=bucket)
        print(f"✓ Created bucket '{bucket}'")
    print(f"✓ Bucket '{bucket}' ready")


def main() -> None:
    config = PipelineConfig.load(ROOT / "config" / "test.toml", ".env.local.example")

    r2 = R2.make_client(config)
    ensure_minio(config.endpoint_url)
    ensure_bucket(r2, config.r2_bucket_name)


if __name__ == "__main__":
    main()
