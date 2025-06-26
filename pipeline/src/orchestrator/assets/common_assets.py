import dagster as dg
from transformations.utils.io import download_files_from_drive
from transformations.utils.env import load_env_vars
from pathlib import Path



@dg.asset(
    kinds={"bronze"}
)
def google_drive_files() -> str:
    env_vars = load_env_vars()
    download_files_from_drive(
        input_data_folder=Path("data/bronze/landing"),
        env_vars=env_vars,
    )
    return "data/bronze/landing"

@dg.asset(
    kinds={"bronze"}
)
def landing_zone() -> str:
    return "data/bronze/landing"