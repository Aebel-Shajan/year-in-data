
import os
from dotenv import load_dotenv
import logging
from typing import Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class EnvVars(BaseModel):
    DRIVE_SHARE_URL: Optional[str] = None
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_USERNAME: Optional[str] = None


def load_env_vars() -> EnvVars:
    load_dotenv(override=True)
    env_vars = EnvVars(**os.environ)
    env_vars = env_vars.model_dump()
    for var in EnvVars.model_fields.keys():
        if env_vars[var] is None:
            logger.warning(f"Expected {var} to be in .env!")
    return env_vars
