from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

_ROOT = Path(__file__).parent.parent.parent


# ── YAML schema models ────────────────────────────────────────────────────────

class _R2Config(BaseModel):
    bucket_name: str
    web_bucket_name: str


class _GithubConfig(BaseModel):
    username: str


class _ExtractConfig(BaseModel):
    sources_to_extract: list[str] = []
    extract_from: str = ""
    extract_to: str = ""


class _AggregateConfig(BaseModel):
    aggregate_from: str = ""
    aggregate_to: str = ""


class _PipelineSection(BaseModel):
    jobs_to_run: list[str] = []
    extract: _ExtractConfig = _ExtractConfig()
    aggregate: _AggregateConfig = _AggregateConfig()


class ConfigFile(BaseModel):
    """Pydantic model for config.yaml — use model_json_schema() to regenerate schema.json."""
    r2: _R2Config
    github: _GithubConfig
    pipeline: _PipelineSection = _PipelineSection()


# ── Runtime config ────────────────────────────────────────────────────────────

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
    garmin_username: str = ""
    garmin_password: str = ""

    def __init__(self, env_file: str = ".env", **kwargs):
        super().__init__(_env_file=env_file, **kwargs)


@dataclass
class PipelineConfig:
    """Project-level settings — loaded from config.yaml and env file."""

    r2_bucket_name: str
    web_bucket_name: str
    github_username: str
    secrets: Secrets
    endpoint_url: str
    extract_from: str | None
    extract_to: str | None
    jobs_to_run: list[str] = field(default_factory=list)
    sources_to_extract: list[str] = field(default_factory=list)

    @staticmethod
    def load(
        config_path: Path = _ROOT / "config" / "config.yaml",
        env_path: str = ".env"
    ) -> "PipelineConfig":
        with open(config_path) as f:
            raw = yaml.safe_load(f)
        cfg = ConfigFile.model_validate(raw)
        secrets = Secrets(env_file=env_path)

        return PipelineConfig(
            r2_bucket_name=cfg.r2.bucket_name,
            web_bucket_name=cfg.r2.web_bucket_name,
            github_username=cfg.github.username,
            secrets=secrets,
            endpoint_url=secrets.r2_endpoint_url,
            sources_to_extract=_parse_list("SOURCES_TO_EXTRACT") or cfg.pipeline.extract.sources_to_extract,
            jobs_to_run=_parse_list("JOBS_TO_RUN") or cfg.pipeline.jobs_to_run,
            extract_from=cfg.pipeline.extract.extract_from or None,
            extract_to=cfg.pipeline.extract.extract_to or None,
        )


def _parse_list(env_var: str) -> list[str]:
    """Parse a comma-separated env var into a list, returning [] if unset or empty."""
    raw = os.getenv(env_var, "").strip()
    return [t.strip() for t in raw.split(",") if t.strip()]
