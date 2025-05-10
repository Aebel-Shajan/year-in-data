

from pathlib import Path
import shutil
import pandas as pd
from yd_extractor.fitbit.utils import extract_json_file_data
from yd_extractor.utils.pandas import convert_columns_to_numeric, validate_columns
from yd_extractor.utils.utils import extract_specific_files_flat
import logging

logger = logging.getLogger(__name__)


def extract_exercise(folder_path: str) -> pd.DataFrame:
    """Extract exercise data from files from the folder path. The files have the name 
    format "exercise-YYYY-MM-DD.json".

    Parameters
    ----------
    folder_path : str
        Path to folder containing jsons with exercise data.
    """
    keys_to_keep = [
        "activityName",
        "averageHeartRate",
        "calories",
        "distance",
        "activeDuration",
        "startTime",
        "pace"
    ]
    df_raw = extract_json_file_data(
        folder_path,
        file_name_prefix="exercise",
        keys_to_keep=keys_to_keep
    )
    return df_raw


def transform_exercise(df: pd.DataFrame) -> pd.DataFrame:
    """Apply transformations to exercise dataframe.

    Parameters
    ----------
    sleep_df : pd.DataFrame
        Raw Fibit dataframe containing columns:
            `["startTime", "distance"]`
    """
    keys_to_keep = [
        "activityName",
        "averageHeartRate",
        "calories",
        "distance",
        "activeDuration",
        "startTime",
        "pace"
    ]
    validate_columns(df, keys_to_keep)
    df = df[keys_to_keep]
    df = df.rename(
        columns={
            "activityName": "activity_name",
            "averageHeartRate": "average_heart_rate",
            "activeDuration": "active_duration",
            "startTime": "start_time",
        }
    )
    df = convert_columns_to_numeric(
        df,
        columns=[
            "average_heart_rate",
            "calories",
            "distance",
            "active_duration",
            "pace"
        ]
    )
    df.loc[:, "date"] = pd.to_datetime(df["start_time"], format="%m/%d/%y %H:%M:%S").dt.date
    df.loc[:, "start_time"] = pd.to_datetime(df["start_time"], format="%m/%d/%y %H:%M:%S").dt.time
    
    df["distance"] = df["distance"].round(2)
    # only include exercises which lasted more than 15 mins
    df = df[df["active_duration"] >= 15 * 1000 * 60]
    return df


def process_exercise(
    inputs_folder: Path,
    zip_path: Path,
    cleanup: bool=True
) -> pd.DataFrame:
    
    # Unzip and extract jsons from zip file.
    logger.info("Processing fitbit exercises...")
    data_folder = inputs_folder / "exercise"
    extract_specific_files_flat(
        zip_file_path=zip_path,
        prefix="Takeout/Fitbit/Global Export Data/exercise",
        output_path=data_folder
    )
    df_raw = extract_exercise(data_folder)
    
    df_standardized = transform_exercise(df_raw)
    
    logger.info("Finished processing fitbit exercises...")
    
    if cleanup:
        logger.info(f"Removing folder {data_folder} from zip...")
        shutil.rmtree(data_folder)
        
    return df_standardized


