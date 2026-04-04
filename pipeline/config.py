from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

_ROOT = Path(__file__).parent.parent


class Secrets(BaseSettings):
    """Credentials and machine-specific overrides — loaded from env / .env file."""

    model_config = SettingsConfigDict(env_file_encoding="utf-8", extra="ignore")

    r2_endpoint_url: str
    r2_access_key_id: str
    r2_secret_access_key: str
    cloudflare_api_token: str
    github_token: str
    gym_group_username: str = ""
    gym_group_password: str = ""

    def __init__(self, env_file: str = ".env", **kwargs):
        super().__init__(_env_file=env_file, **kwargs)


@dataclass
class PipelineConfig:
    """Project-level settings — loaded from config.toml and env file."""

    runtime_env: Literal["local", "github_actions"]
    r2_bucket_name: str
    web_bucket_name: str
    github_username: str
    secrets: Secrets
    endpoint_url: str
    tags_to_run: list[str] = field(default_factory=list)    # empty = run all
    tags_to_ignore: list[str] = field(default_factory=list)

    @staticmethod
    def load(
        config_path: Path = _ROOT / "config" / "config.toml",
        env_path: str = ".env"
    ) -> "PipelineConfig":
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
        secrets = Secrets(env_file=env_path)
        sources = data.get("sources", {})

        return PipelineConfig(
            runtime_env=data["general"]["runtime_env"],
            r2_bucket_name=data["r2"]["bucket_name"],
            web_bucket_name=data["r2"]["web_bucket_name"],
            github_username=data["github"]["username"],
            secrets=secrets,
            endpoint_url=secrets.r2_endpoint_url,
            tags_to_run=_parse_tags("PIPELINE_TAGS_TO_RUN") or sources.get("tags_to_run", []),
            tags_to_ignore=_parse_tags("PIPELINE_TAGS_TO_IGNORE") or sources.get("tags_to_ignore", [])
        )


def _parse_tags(env_var: str) -> list[str]:
    """Parse a comma-separated env var into a list of tags, returning [] if unset or empty."""
    raw = os.getenv(env_var, "").strip()
    return [t.strip() for t in raw.split(",") if t.strip()]
