"""
Empty and delete both R2 buckets (pipeline + web). This is irreversible.

  uv run python scripts/delete_bucket.py

Credentials and bucket names are read from config/config.yaml and .env.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.common.config import PipelineConfig
from pipeline.common.r2 import make_client, make_web_client, list_keys
ROOT = Path(__file__).parent.parent


def delete_bucket(r2, bucket: str) -> None:
    print(f"Emptying '{bucket}'...")
    keys = list_keys(r2, "")
    if keys:
        r2.client.delete_objects(  # type: ignore[attr-defined]
            Bucket=bucket,
            Delete={"Objects": [{"Key": k} for k in keys]},
        )
        print(f"  deleted {len(keys)} object(s)")
    else:
        print("  bucket already empty")
    r2.client.delete_bucket(Bucket=bucket)  # type: ignore[attr-defined]
    print(f"✓ Bucket '{bucket}' deleted")


def main() -> None:
    config = PipelineConfig.load(ROOT / "config" / "test.yaml", ".env.local.example")
    buckets = f"'{config.r2_bucket_name}' and '{config.web_bucket_name}'"

    print(f"This will permanently delete all objects and buckets: {buckets}.")
    confirm = input("Type DELETE to confirm: ").strip()
    if confirm != "DELETE":
        print("Aborted.")
        sys.exit(1)

    delete_bucket(make_client(config), config.r2_bucket_name)
    delete_bucket(make_web_client(config), config.web_bucket_name)


if __name__ == "__main__":
    main()
