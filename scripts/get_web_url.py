"""
Print the public development URL (pub-*.r2.dev) of the web R2 bucket.

Used by the deploy workflow to inject VITE_R2_PUBLIC_URL at build time.

  uv run python scripts/get_web_url.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx

from pipeline.common.config import PipelineConfig


def main() -> None:
    config = PipelineConfig.load()
    account_id = config.endpoint_url.removeprefix("https://").split(".")[0]

    resp = httpx.get(
        f"https://api.cloudflare.com/client/v4/accounts/{account_id}/r2/buckets/{config.web_bucket_name}/domains/managed",
        headers={"Authorization": f"Bearer {config.secrets.cloudflare_api_token}"},
    )
    resp.raise_for_status()

    result = resp.json().get("result", {})
    domain = result.get("domain")
    if not domain:
        print(f"✗ Could not find public URL in response: {result}", file=sys.stderr)
        print("  Run 'make setup-r2' first to enable public access.", file=sys.stderr)
        sys.exit(1)

    print(f"https://{domain}")


if __name__ == "__main__":
    main()
