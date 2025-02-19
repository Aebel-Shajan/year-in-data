from yd_pipeline.process_data.strong import (
    process_strong_data, 
    get_distinct_exercises,
    get_distinct_workouts
)
from yd_pipeline.download_from_drive import download_data_from_drive
from yd_pipeline.process_data.kindle import process_kindle_data, get_distinct_books
from yd_pipeline.process_data.github import process_github_data, get_distinct_repos
from yd_pipeline.process_data.fitbit import (
    process_sleep_data, 
    process_calorie_data,
    process_steps,
    process_running
)
from yd_pipeline.utils import (
    write_db_to_jsons,
    get_latest_file,
    unzip_file
)
from pathlib import Path
import os
from dotenv import load_dotenv
import zipfile
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s -%(levelname)s -on line: %(lineno)d -%(message)s')
logger = logging.getLogger() 


# Load environment variables
logger.info("Loading environement variables...")
load_dotenv()
share_url = os.getenv("DRIVE_SHARE_URL")
github_token = os.getenv("GITHUB_TOKEN")
if (share_url is None):
    raise Exception("Couldn't find google drive share link")

root_dir = Path(__file__).resolve().parent
data_file_path = root_dir / "data" / "input"
os.makedirs(data_file_path, exist_ok=True)
os.makedirs(root_dir/"data"/"output", exist_ok=True)


# Download data from google drive
logger.info("Downloading data from google drive...")
download_data_from_drive(os.getenv("DRIVE_SHARE_URL"))


# ETL strong data
logger.info("Starting ETL for strong data...")
latest_strong_csv = get_latest_file(
    folder_path=data_file_path,
    file_name_glob="strong*.csv"
)
with open(latest_strong_csv) as csv:
    logger.info(f"Processing strong file: {latest_strong_csv}")
    process_strong_data(csv)
    get_distinct_workouts()
    get_distinct_exercises()


# ETL kindle data
# Find the most recent Kindle zip file
logger.info("Starting ETL for kindle data...")
latest_kindle_zip = get_latest_file(
    folder_path=data_file_path,
    file_name_glob="Kindle*.zip"
)
kindle_folder_path = (
    data_file_path
    / "Kindle"
)
unzip_file(
    zip_file_path=latest_kindle_zip,
    output_path=kindle_folder_path
)
kindle_file_path = (
    kindle_folder_path
    / "Kindle.ReadingInsights"
    / "datasets"
    / "Kindle.reading-insights-sessions_with_adjustments"
    / "Kindle.reading-insights-sessions_with_adjustments.csv"
)
with open(kindle_file_path) as csv:
    process_kindle_data(csv)
    get_distinct_books()
    

# ETL github data
# I WILL NOT COMMIT MY GITHUB TOKEN TO GIT.
# I WILL NOT COMMIT MY GITHUB TOKEN TO GIT.
# I WILL NOT COMMIT MY GITHUB TOKEN TO GIT.
# I WILL NOT COMMIT MY GITHUB TOKEN TO GIT.
# I WILL NOT COMMIT MY GITHUB TOKEN TO GIT.
if (github_token):
    process_github_data("aebel-shajan", github_token)


# ETL fitbit data
latest_google_zip = get_latest_file(
    folder_path=data_file_path,
    file_name_glob="takeout*.zip"
)
google_folder_path = (
    data_file_path
    / "Google"
)
unzip_file(
    zip_file_path=latest_google_zip,
    output_path=google_folder_path
)
fitbit_folder_path = (
    google_folder_path 
    / "Takeout"
    / "Fitbit"
    / "Global Export Data"
) 
process_sleep_data(fitbit_folder_path)
process_calorie_data(fitbit_folder_path)
process_steps(fitbit_folder_path)
process_running(fitbit_folder_path)



# Convert SQLite DB to JSON
logger.info("Writing sqlite db into jsons...")
write_db_to_jsons(
    db_path="./data/output/year_in_data.db",
    output_path="./data/output"
)