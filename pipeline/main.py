import logging
import os
from pathlib import Path


import yd_extractor.fitbit as fitbit_extractor
import yd_extractor.github as github_extractor
import yd_extractor.kindle as kindle_extractor
import yd_extractor.strong as strong_extractor
from yd_extractor.app_usage.screen_time import process_screen_time
from config import config_loader
from yd_extractor.utils.logger import (
    setup_aebels_logger,
)
from yd_extractor.utils.io import download_files_from_drive, get_latest_file, create_load_function

# Create a logger
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)
setup_aebels_logger(
    logger=logger,
    filter_strings=[
        "https://drive.google.com/uc?id"
    ],  # Because gdown leaks google url.
    # resource_monitoring_interval=1.1,
    show_context=False,
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
    load_function = create_load_function(output_data_folder)

    os.makedirs(input_data_folder, exist_ok=True)
    os.makedirs(root_dir / "data" / "output", exist_ok=True)
    os.makedirs(root_dir / "data" / "output" / "metadata", exist_ok=True)
    logger.info(f"Inputs and output data will be stored here: {root_dir / 'data'}")

    if config.download_from_drive:
        try:
            download_files_from_drive(input_data_folder, env_vars)
        except Exception as e:
            logger.exception(f"Error while downloading files from Google Drive")

    # Fitbit
    if fitbit_config.process_fitbit:
        latest_google_zip = get_latest_file(
            folder_path=input_data_folder,
            file_name_glob="takeout*.zip",
        )

        # Calories
        if fitbit_config.process_calories:
            fitbit_extractor.process_calories(
                inputs_folder=input_data_folder,
                zip_path=latest_google_zip,
                cleanup=config.cleanup_unziped_files,
                load_function=load_function,
            )

        # Sleep
        if fitbit_config.process_sleep:
            fitbit_extractor.process_sleep(
                inputs_folder=input_data_folder,
                zip_path=latest_google_zip,
                cleanup=config.cleanup_unziped_files,
                load_function=load_function,
            )

        # Steps
        if fitbit_config.process_steps:
            fitbit_extractor.process_steps(
                inputs_folder=input_data_folder,
                zip_path=latest_google_zip,
                cleanup=config.cleanup_unziped_files,
                load_function=load_function,
            )

        # Exercise
        if fitbit_config.process_exercise:
            fitbit_extractor.process_exercise(
                inputs_folder=input_data_folder,
                zip_path=latest_google_zip,
                cleanup=config.cleanup_unziped_files,
                load_function=load_function,
            )

    # Github
    if config.process_github:
        github_extractor.process_repo_contributions(
            github_token=env_vars["GITHUB_TOKEN"],
            load_function=load_function,
        )

    # Kindle
    if config.process_kindle:
        latest_zip = get_latest_file(
            folder_path=input_data_folder,
            file_name_glob="Kindle*.zip",
        )
        kindle_extractor.process_reading(
            inputs_folder=input_data_folder,
            zip_path=latest_zip,
            cleanup=config.cleanup_unziped_files,
            load_function=load_function,
        )

    # Strong
    if config.process_strong:
        latest_csv = get_latest_file(
            folder_path=input_data_folder,
            file_name_glob="strong*.csv",
        )
        strong_extractor.process_workouts(
            latest_csv,
            load_function,
        )
    
    # App Usage
    if config.process_app_usage:
        screen_time_csv = get_latest_file(
            folder_path=input_data_folder,
            file_name_glob="AUM_V4_Activity*.csv"
        )
        app_info_csv = None
        try:
            app_info_csv = get_latest_file(
                folder_path=input_data_folder,
                file_name_glob="AUM_V4_App*.csv"
            )
        except:
            logger.warning("Couldn't find app info file.")
        
        process_screen_time(
            screen_time_csv,
            app_info_csv,
            load_function=load_function
        )
        

    if config.cleanup_ziped_files:
        for zip_file in input_data_folder.glob("*.zip"):
            zip_file.unlink()
    logger.info("Finished extracting data.")


if __name__ == "__main__":
    config = config_loader.load_config("config/config.toml")
    env_vars = config_loader.load_env_vars()
    run_pipeline(config, env_vars)
