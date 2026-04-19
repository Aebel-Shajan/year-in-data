from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

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

    r2_bucket_name: str
    web_bucket_name: str
    github_username: str
    secrets: Secrets
    endpoint_url: str
    jobs_to_run: list[str] = field(default_factory=list)   # empty = run all

    @staticmethod
    def load(
        config_path: Path = _ROOT / "config" / "config.toml",
        env_path: str = ".env"
    ) -> "PipelineConfig":
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
        secrets = Secrets(env_file=env_path)
        pipeline = data.get("pipeline", {})

        return PipelineConfig(
            r2_bucket_name=data["r2"]["bucket_name"],
            web_bucket_name=data["r2"]["web_bucket_name"],
            github_username=data["github"]["username"],
            secrets=secrets,
            endpoint_url=secrets.r2_endpoint_url,
            jobs_to_run=_parse_list("PIPELINE_JOBS_TO_RUN") or pipeline.get("jobs_to_run", []),
        )


def _parse_list(env_var: str) -> list[str]:
    """Parse a comma-separated env var into a list, returning [] if unset or empty."""
    raw = os.getenv(env_var, "").strip()
    return [t.strip() for t in raw.split(",") if t.strip()]
