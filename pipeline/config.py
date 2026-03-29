from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_ROOT = Path(__file__).parent.parent


class Secrets(BaseSettings):
    """Credentials and machine-specific overrides — loaded from env / .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    r2_account_id: str
    r2_access_key_id: str
    r2_secret_access_key: str
    github_token: str
    gym_group_username: str = ""
    gym_group_password: str = ""
    # Optional: overrides the R2 endpoint (used for local MinIO)
    r2_endpoint_url: str = ""


@dataclass
class Config:
    """Project-level settings — loaded from config.toml."""

    r2_bucket_name: str
    r2_public_url: str
    github_username: str
    run_fitbit: bool
    run_kindle: bool
    run_github: bool
    run_strong: bool
    run_gymgroup: bool

    @staticmethod
    def load(path: Path = _ROOT / "config" / "config.toml") -> "Config":
        with open(path, "rb") as f:
            data = tomllib.load(f)
        return Config(
            r2_bucket_name=data["r2"]["bucket_name"],
            r2_public_url=data["r2"]["public_url"],
            github_username=data["github"]["username"],
            run_fitbit=data["sources"]["fitbit"],
            run_kindle=data["sources"]["kindle"],
            run_github=data["sources"]["github"],
            run_strong=data["sources"]["strong"],
            run_gymgroup=data["sources"]["gymgroup"],
        )
