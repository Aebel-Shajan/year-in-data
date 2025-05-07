import logging
import os
from pathlib import Path
import sys

from dotenv import load_dotenv

import yd_extractor.fitbit as fitbit_extractor
import yd_extractor.github as github_extractor
import yd_extractor.kindle as kindle_extractor
import yd_extractor.strong as strong_extractor
import gdown

from yd_extractor.utils.colored_logger import ColoredFormatter
from yd_extractor.utils.utils import get_latest_file
from typing import Optional, TypedDict

# Create a logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create a console handler
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)

# Define a formatter with equal-width columns
formatter = ColoredFormatter('%(asctime)s | %(levelname)-8s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)


config = {
    "download_from_drive": False,
    "cleanup_unziped_files": False,
    "cleanup_ziped_files": False,
    "fitbit_config": {
        "process_calories": False,
        "process_sleep": False,
        "process_steps": False,
        "process_exercise": False,
    },
    "process_github": False,
    "process_kindle": True,
    "process_strong": True,
}

class EnvVars(TypedDict):
    DRIVE_SHARE_URL: Optional[str]
    GITHUB_TOKEN:  Optional[str]
    GITHUB_USERNAME:  Optional[str]

if __name__ == "__main__":
    # Unpack config
    cleanup_ziped_files = config["cleanup_ziped_files"]
    cleanup_unziped_files = config["cleanup_unziped_files"]
    fitbit_config = config["fitbit_config"]
    
    # Read in .env
    logger.info("Loading environement variables...")
    load_dotenv(override=True)
    env_vars: EnvVars = {
        "DRIVE_SHARE_URL": os.environ.get("DRIVE_SHARE_URL"),
        "GITHUB_TOKEN": os.environ.get("GITHUB_TOKEN"),
        "GITHUB_USERNAME": os.environ.get("GITHUB_USERNAME")
    }
    for var in env_vars:
        if env_vars[var] is None:
            logger.warning("Expected {var} to be in .env!")

    # Setup folder structure
    root_dir = Path(__file__).resolve().parent.parent
    input_data_folder = root_dir / "data" / "input"
    output_data_folder = root_dir / "data" / "output"
    os.makedirs(input_data_folder, exist_ok=True)
    os.makedirs(root_dir/"data"/"output", exist_ok=True)
    logger.info(f"Inputs and output data will be stored here: {root_dir / 'data'}")
    
    if config["download_from_drive"]:
        if (env_vars["DRIVE_SHARE_URL"] is None):
            raise Exception("Expected DRIVE_SHARE_URL in .env folder!")
        logger.info("Downloading data from google drive...")
        gdown.download_folder(
            url=env_vars["DRIVE_SHARE_URL"],
            output=str(input_data_folder.absolute()),
            use_cookies=False
        )
    
    # Fitbit
    if any(list(fitbit_config.values())):
        latest_google_zip = get_latest_file(
            folder_path=input_data_folder,
            file_name_glob="takeout*.zip"
        )
        fitbit_relative_folder = "Takeout/Fitbit/Global Export Data/"
        fitbit_absolute_path = input_data_folder / fitbit_relative_folder
        
        # Calories
        if fitbit_config["process_calories"]:
            df = fitbit_extractor.process_calories(
                inputs_folder=input_data_folder, 
                zip_path=latest_google_zip,
                cleanup=cleanup_unziped_files
            )
            df.to_csv(output_data_folder / "fitbit_calories.csv", index=False)


        # Sleep
        if fitbit_config["process_sleep"]:
            df = fitbit_extractor.process_sleep(
                inputs_folder=input_data_folder,
                zip_path=latest_google_zip,
                cleanup=cleanup_unziped_files
            )
            df.to_csv(output_data_folder / "fitbit_sleep.csv", index=False)


        # Steps
        if fitbit_config["process_steps"]:
            df = fitbit_extractor.process_steps(
                inputs_folder=input_data_folder,
                zip_path=latest_google_zip,
                cleanup=cleanup_unziped_files
            )
            df.to_csv(output_data_folder / "fitbit_steps.csv", index=False)

                
        # Exercise
        if fitbit_config["process_exercise"]:
            df = fitbit_extractor.process_exercise(
                inputs_folder=input_data_folder,
                zip_path=latest_google_zip,
                cleanup=cleanup_unziped_files
            )
            df.to_csv(output_data_folder / "fitbit_exercise.csv", index=False)
        
    # Github
    if (config["process_github"]): 
        if env_vars["GITHUB_TOKEN"] is None or env_vars["GITHUB_USERNAME"] is None:
            logger.error(
                "Couldn't process github data due to missing environment variables!"
            ) 
        df = github_extractor.process_repo_contributions(
            github_token=env_vars["GITHUB_TOKEN"]
        )
        df.to_csv(output_data_folder / "repo_contributions.csv", index=False)
    
    # Kindle
    if config["process_kindle"]:
        latest_zip = get_latest_file(
            folder_path=input_data_folder,
            file_name_glob="Kindle*.zip"
        )
        df = kindle_extractor.process_reading(
            inputs_folder=input_data_folder,
            zip_path=latest_zip,
            cleanup=config["cleanup_unziped_files"]
        )
        df.to_csv(output_data_folder / "reading.csv", index=False)
        
    # Strong
    if config["process_strong"]:
        latest_csv = get_latest_file(
            folder_path=input_data_folder,
            file_name_glob="strong*.csv"
        )
        with open(latest_csv) as csv:
            df = strong_extractor.process_workouts(csv)
            df.to_csv(output_data_folder / "strong_workouts.csv")
    
    logger.info("Finished extracting data.")