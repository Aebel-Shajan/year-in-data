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

import sys
import tempfile
from pathlib import Path

import gdown
from dotenv import dotenv_values

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from pipeline.config import PipelineConfig
from pipeline.r2 import make_client, upload_bytes, exists

def main() -> None:
    config = PipelineConfig.load()
    r2 = make_client(config)

    ASSET_NAMES = ["fitbit", "kindle", "strong"]
    
    # Get drive URL from environment
    env = dotenv_values(ROOT / ".env")
    drive_url = env.get("DRIVE_SHARE_URL")
    if not drive_url:
        print("✗ DRIVE_SHARE_URL not set in .env")
        sys.exit(1)
    
    print(f"Syncing from {drive_url}")
    
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        
        for asset in ASSET_NAMES:
            asset_dir = tmp_path / asset
            asset_dir.mkdir()
            
            # Download all files from this asset's Drive folder
            folder_url = f"{drive_url}/{asset}"
            try:
                gdown.download_folder(folder_url, output=str(asset_dir), quiet=True)
            except Exception as e:
                print(f"  skipping {asset}: {e}")
                continue
            
            # Upload new files to R2 inbox
            for file_path in asset_dir.rglob("*"):
                if file_path.is_file():
                    relative_path = file_path.relative_to(asset_dir)
                    r2_key = f"bronze/inbox/{asset}/{relative_path}"
                    
                    if exists(r2, r2_key):
                        print(f"  skipping {r2_key} (already exists)")
                        continue
                    
                    with open(file_path, "rb") as f:
                        data = f.read()
                    
                    upload_bytes(r2, r2_key, data)
                    print(f"  uploaded {r2_key}")


if __name__ == "__main__":
    main()
