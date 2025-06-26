import logging

import pandas as pd
import pandera as pa
from pandera.typing.pandas import DataFrame

from transformations.fitbit.schemas import FitbitExercise, RawFitbitExercise
from transformations.fitbit.utils import extract_json_file_data
from transformations.utils.io import extract_specific_files_flat

logger = logging.getLogger(__name__)


def extract_exercise_jsons(zip_path: str, data_folder: str):
    extract_specific_files_flat(
        zip_file_path=zip_path,
        prefix="Takeout/Fitbit/Global Export Data/exercise",
        output_path=data_folder,
    )
    return data_folder

@pa.check_types
def extract_exercise_jsons_into_dataframe(data_folder: str) -> DataFrame[RawFitbitExercise]:
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

