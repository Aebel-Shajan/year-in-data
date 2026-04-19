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

from pipeline.common.bucket_setup import create_inboxes, ensure_bucket, set_public_policy
from pipeline.common.config import PipelineConfig
from pipeline.common.r2 import make_client, make_web_client


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



def main() -> None:
    config = PipelineConfig.load(ROOT / "config" / "test.toml", ".env.local.example")
    r2 = make_client(config)
    web_r2 = make_web_client(config)

    ensure_minio(config.endpoint_url)
    ensure_bucket(r2, config.r2_bucket_name)
    ensure_bucket(web_r2, config.web_bucket_name)
    set_public_policy(config.endpoint_url,config.web_bucket_name)
    create_inboxes(r2)


if __name__ == "__main__":
    main()
