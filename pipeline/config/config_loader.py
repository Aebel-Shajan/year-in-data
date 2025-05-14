import logging
import os
from typing import Optional

import toml
from dotenv import load_dotenv
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class FitbitConfig(BaseModel):
    process_fitbit: bool
    process_calories: bool
    process_sleep: bool
    process_steps: bool
    process_exercise: bool


class EnvVars(BaseModel):
    DRIVE_SHARE_URL: Optional[str] = None
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_USERNAME: Optional[str] = None


# Pydantic model to validate and parse config
class PipelineConfig(BaseModel):
    download_from_drive: bool
    cleanup_unziped_files: bool
    cleanup_ziped_files: bool
    fitbit_config: FitbitConfig
    process_github: bool
    process_kindle: bool
    process_strong: bool

    @classmethod
    def from_toml(cls, file_path: str) -> "PipelineConfig":
        """Load and validate the configuration file."""
        config_data = toml.load(file_path)
        return cls(**config_data)


# Load the config from the TOML file
def load_config(config_path: str) -> PipelineConfig:
    return PipelineConfig.from_toml(config_path)


def load_env_vars() -> EnvVars:
    load_dotenv(override=True)
    env_vars = EnvVars(**os.environ)
    env_vars = env_vars.model_dump()
    for var in EnvVars.model_fields.keys():
        if env_vars[var] is None:
            logger.warning(f"Expected {var} to be in .env!")
    return env_vars
