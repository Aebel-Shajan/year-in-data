
import os
from dotenv import load_dotenv
import logging
from typing import Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class EnvVars(BaseModel):
    DRIVE_SHARE_URL: Optional[str] = None
    GITHUB_TOKEN: Optional[str] = None
    DAGSTER_HOME: Optional[str] = None


def load_env_vars() -> EnvVars:
    load_dotenv(override=True)
    env_vars = EnvVars(**os.environ)
    for field, value in env_vars.model_dump().items():
        if value is None:
            logger.warning(f"Expected {field} to be in .env!")
    return env_vars
