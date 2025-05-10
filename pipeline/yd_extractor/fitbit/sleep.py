from pathlib import Path
import shutil
import pandas as pd

from yd_extractor.utils.pandas import validate_columns
from yd_extractor.utils.utils import extract_specific_files_flat

from yd_extractor.fitbit.utils import extract_json_file_data
import logging
logger = logging.getLogger(__name__)

def extract_sleep(folder_path: str) -> pd.DataFrame:
    """Extract sleep data from files from the folder path. The files have the name format
    "sleep-YYYY-MM-DD.json".

    Parameters
    ----------
    folder_path : str
        Path to folder containing jsons with sleep data.
    """
    keys_to_keep = [
        "logId",
        "dateOfSleep",
        "startTime",
        "endTime",
        "duration",
        "minutesToFallAsleep",
        "minutesAsleep",
        "minutesAwake",
        "minutesAfterWakeup",
        "timeInBed",
        "efficiency",
    ]
    df_sleep_raw = extract_json_file_data(
        folder_path,
        file_name_prefix="sleep",
        keys_to_keep=keys_to_keep
    )
    return df_sleep_raw
    
# no standardise 😔
def transform_sleep(df: pd.DataFrame) -> pd.DataFrame:
    """Apply transformations to sleep dataframe, then saves dataframe in table:
    `year_in_data.fitbit_sleep_data_processed`

    Parameters
    ----------
    sleep_df : pd.DataFrame
        Raw Fibit sleep dataframe containing columns:
            `["dateOfSleep", "startTime", "endTime", "duration"]`

    """
    # Select only important data for current analysis
    columns_to_keep = ["dateOfSleep", "startTime", "endTime", "duration"]
    validate_columns(df, columns_to_keep)
    df = df[columns_to_keep]
    df = df.rename(
        columns={
            "dateOfSleep": "date",
            "startTime": "start_time",
            "endTime": "end_time",
            "duration": "total_duration",
        }
    )
    df["total_duration_hours"] = df["total_duration"].apply(
        lambda x: round(x / (1000 * 60 * 60), 2)
    )
    df = df.drop(columns=["total_duration"])
    df.loc[:, "date"] = pd.to_datetime(df["date"]).dt.date
    df.loc[:, "start_time"] = pd.to_datetime(df["start_time"]).dt.time
    df.loc[:, "end_time"] = pd.to_datetime(df["end_time"]).dt.time
    df = df.groupby(["date"]).aggregate(
        {"start_time": "min", "end_time": "max", "total_duration_hours": "sum"}
    ).reset_index()
    return df


def process_sleep(
    inputs_folder: Path,
    zip_path: Path,
    cleanup: bool=True
) -> pd.DataFrame:
    # Unzip and extract calories jsons from zip file.
    logger.info("Processing fitbit sleep...")
    data_folder = inputs_folder / "sleep"
    extract_specific_files_flat(
        zip_file_path=zip_path,
        prefix="Takeout/Fitbit/Global Export Data/sleep",
        output_path=data_folder
    )
    df_raw = extract_sleep(data_folder)
    
    df_standardized = transform_sleep(df_raw)
    
    logger.info("Finished processing fitbit sleep")
    
    
    if cleanup:
        logger.info(f"Removing folder {data_folder} from zip...")
        shutil.rmtree(data_folder)
        
    return df_standardized