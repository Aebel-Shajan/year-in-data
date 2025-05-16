import logging
import shutil
from pathlib import Path
from typing import Callable, Optional

import pandas as pd
import pandera as pa
from pandera.typing.pandas import DataFrame

from yd_extractor.utils.pipeline_stage import PipelineStage
from yd_extractor.fitbit.schemas import FitbitExercise, RawFitbitExercise
from yd_extractor.fitbit.utils import extract_json_file_data
from yd_extractor.utils.pandas import (convert_columns_to_numeric,
                                       validate_columns)
from yd_extractor.utils.io import extract_specific_files_flat

logger = logging.getLogger(__name__)


@pa.check_types
def extract_exercise(data_folder: str, zip_path: str) -> DataFrame[RawFitbitExercise]:
    """Extract exercise data from files from the folder path. The files have the name
    format "exercise-YYYY-MM-DD.json".

    Parameters
    ----------
    folder_path : str
        Path to folder containing jsons with exercise data.
    """
    extract_specific_files_flat(
        zip_file_path=zip_path,
        prefix="Takeout/Fitbit/Global Export Data/exercise",
        output_path=data_folder,
    )
    keys_to_keep = [
        "activityName",
        "averageHeartRate",
        "calories",
        "distance",
        "activeDuration",
        "startTime",
        "pace",
    ]
    df = extract_json_file_data(
        data_folder, file_name_prefix="exercise", keys_to_keep=keys_to_keep
    )
    df = RawFitbitExercise.validate(df)
    return df


def transform_exercise(df: DataFrame[RawFitbitExercise]) -> DataFrame[FitbitExercise]:
    """Apply transformations to exercise dataframe.

    Parameters
    ----------
    sleep_df : pd.DataFrame
        Raw Fibit dataframe containing columns:
            `["startTime", "distance"]`
    """
    df = df.rename(
        columns={
            "activityName": "activity_name",
            "averageHeartRate": "average_heart_rate_bpm",
            "activeDuration": "active_duration_minutes",
            "startTime": "start_time",
            "distance": "distance_km",
            "pace": "pace_seconds_per_km",
        }
    )
    df["distance_km"] = df["distance_km"].fillna(0)
    df["pace_seconds_per_km"] = df["pace_seconds_per_km"].fillna(0)
    df = df[df["average_heart_rate_bpm"] != 0]
    df = df[df["distance_km"] != 0]
    df.loc[:, "date"] = pd.to_datetime(
        df["start_time"], format="%m/%d/%y %H:%M:%S"
    ).dt.date
    df["date"] = pd.to_datetime(df["date"])
    df.loc[:, "start_time"] = pd.to_datetime(
        df["start_time"], format="%m/%d/%y %H:%M:%S"
    ).dt.time
    df["pace_minutes_per_km"] = df["pace_seconds_per_km"] / 60
    df["distance_km"] = df["distance_km"].round(2)
    # only include exercises which lasted more than 15 mins
    df = df[df["active_duration_minutes"] >= 15 * 1000 * 60]

    df = df[
        [
            "date",
            "activity_name",
            "average_heart_rate_bpm",
            "distance_km",
            "calories",
            "active_duration_minutes",
            "start_time",
            "pace_minutes_per_km",
        ]
    ]
    df = FitbitExercise.validate(df)
    return df


def process_exercise(
    inputs_folder: Path,
    zip_path: Path,
    cleanup: bool = True,
    load_function: Optional[Callable[[pd.DataFrame, str], None]] = None,
) -> pd.DataFrame:

    # Unzip and extract jsons from zip file.
    data_folder = inputs_folder / "exercise"
    
    with PipelineStage(logger, "fitbit_exercise"):
        df = extract_exercise(data_folder, zip_path)
        df = transform_exercise(df)
        if load_function:
            load_function(df, "fitbit_exercise", FitbitExercise)


    if cleanup:
        logger.info(f"Removing folder {data_folder} from zip...")
        shutil.rmtree(data_folder)

    return df
