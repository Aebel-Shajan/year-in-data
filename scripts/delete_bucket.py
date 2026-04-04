"""
Empty and delete the R2 bucket. This is irreversible.

  uv run python scripts/delete_bucket.py

Credentials and bucket name are read from config/config.toml and .env.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.config import PipelineConfig
from pipeline.r2 import make_client, list_keys


def main() -> None:
    config = PipelineConfig.load()
    r2 = make_client(config)
    bucket = config.r2_bucket_name

    print(f"This will permanently delete all objects and the bucket '{bucket}'.")
    confirm = input("Type the bucket name to confirm: ").strip()
    if confirm != bucket:
        print("Aborted.")
        sys.exit(1)

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


if __name__ == "__main__":
    main()
