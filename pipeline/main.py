import logging
import os
from pathlib import Path

import yd_extractor.fitbit as fitbit_extractor
import yd_extractor.github as github_extractor
import yd_extractor.kindle as kindle_extractor
import yd_extractor.strong as strong_extractor
import gdown

from yd_extractor.utils.logger import setup_aebels_logger, redirect_output_to_logger
from yd_extractor.utils.utils import get_latest_file
from config import config_loader

# Create a logger
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)
setup_aebels_logger(
    logger=logger,
    filter_strings=[
        "https://drive.google.com/uc?id"
    ],  # Because gdown leaks google url.
    # resource_monitoring_interval=1.1,
    show_context=False
)


def download_files_from_drive(input_data_folder: Path, env_vars: config_loader.EnvVars):
    if env_vars["DRIVE_SHARE_URL"] is None:
        raise Exception("Expected DRIVE_SHARE_URL in .env folder!")
    logger.info("Downloading data from google drive...")

    with redirect_output_to_logger(logger, stderr_level=logging.INFO, name="gdown"):
        gdown.download_folder(
            url=env_vars["DRIVE_SHARE_URL"],
            output=str(input_data_folder.absolute()),
            use_cookies=False,
        )


def run_pipeline(
    config: config_loader.PipelineConfig,
    env_vars: config_loader.EnvVars,
):
    # Unpack config
    fitbit_config = config.fitbit_config

    # Setup folder structure
    root_dir = Path(__file__).resolve().parent
    input_data_folder = root_dir / "data" / "input"
    output_data_folder = root_dir / "data" / "output"
    os.makedirs(input_data_folder, exist_ok=True)
    os.makedirs(root_dir / "data" / "output", exist_ok=True)
    logger.info(f"Inputs and output data will be stored here: {root_dir / 'data'}")

    if config.download_from_drive:
        try:
            download_files_from_drive(input_data_folder, env_vars)
        except Exception as e:
            logger.exception(f"Error while downloading files from Google Drive")

    # Fitbit
    if fitbit_config.process_fitbit:
        try:
            latest_google_zip = get_latest_file(
                folder_path=input_data_folder,
                file_name_glob="takeout*.zip",
            )

            # Calories
            if fitbit_config.process_calories:
                df = fitbit_extractor.process_calories(
                    inputs_folder=input_data_folder,
                    zip_path=latest_google_zip,
                    cleanup=config.cleanup_unziped_files,
                )
                df.to_csv(output_data_folder / "fitbit_calories.csv", index=False)

            # Sleep
            if fitbit_config.process_sleep:
                df = fitbit_extractor.process_sleep(
                    inputs_folder=input_data_folder,
                    zip_path=latest_google_zip,
                    cleanup=config.cleanup_unziped_files,
                )
                df.to_csv(output_data_folder / "fitbit_sleep.csv", index=False)

            # Steps
            if fitbit_config.process_steps:
                df = fitbit_extractor.process_steps(
                    inputs_folder=input_data_folder,
                    zip_path=latest_google_zip,
                    cleanup=config.cleanup_unziped_files,
                )
                df.to_csv(output_data_folder / "fitbit_steps.csv", index=False)

            # Exercise
            if fitbit_config.process_exercise:
                df = fitbit_extractor.process_exercise(
                    inputs_folder=input_data_folder,
                    zip_path=latest_google_zip,
                    cleanup=config.cleanup_unziped_files,
                )
                df.to_csv(output_data_folder / "fitbit_exercise.csv", index=False)
        except Exception as e:
            logger.exception(f"Error whilst trying process fitbit data")

    # Github
    if config.process_github:
        try:
            if env_vars["GITHUB_TOKEN"] is None or env_vars["GITHUB_USERNAME"] is None:
                error_message = (
                    "Couldn't process github data due to missing environment variables!"
                )
                raise Exception(error_message)
            df = github_extractor.process_repo_contributions(
                github_token=env_vars["GITHUB_TOKEN"]
            )
            df.to_csv(output_data_folder / "repo_contributions.csv", index=False)
        except Exception as e:
            logger.exception(f"Error whilst trying to process GitHub data")

    # Kindle
    if config.process_kindle:
        try:
            latest_zip = get_latest_file(
                folder_path=input_data_folder, file_name_glob="Kindle*.zip"
            )
            df = kindle_extractor.process_reading(
                inputs_folder=input_data_folder,
                zip_path=latest_zip,
                cleanup=config.cleanup_unziped_files,
            )
            df.to_csv(output_data_folder / "reading.csv", index=False)
        except Exception as e:
            logger.exception(f"Error whilst trying to process Kindle data")

    # Strong
    if config.process_strong:
        try:
            latest_csv = get_latest_file(
                folder_path=input_data_folder, file_name_glob="strong*.csv"
            )
            with open(latest_csv) as csv:
                df = strong_extractor.process_workouts(csv)
                df.to_csv(output_data_folder / "strong_workouts.csv")
        except Exception as e:
            logger.exception(f"Error whilst trying to process Strong data")

    if config.cleanup_ziped_files:
        for zip_file in input_data_folder.glob("*.zip"):
            zip_file.unlink()
    logger.info("Finished extracting data.")


if __name__ == "__main__":
    config = config_loader.load_config("config/config.toml")
    env_vars = config_loader.load_env_vars()
    run_pipeline(config, env_vars)
