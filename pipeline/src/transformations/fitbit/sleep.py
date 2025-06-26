import logging
from pathlib import Path

import pandas as pd
import pandera as pa
from pandera.typing.pandas import DataFrame

from transformations.fitbit.schemas import FitbitSleep, RawFitbitSleep
from transformations.fitbit.utils import extract_json_file_data
from transformations.utils.io import extract_specific_files_flat

logger = logging.getLogger(__name__)

def extract_sleep_jsons(zip_path: str, output_folder: str):
    extract_specific_files_flat(
        zip_file_path=zip_path,
        prefix="Takeout/Fitbit/Global Export Data/sleep",
        output_path=output_folder,
    )
    return output_folder


@pa.check_types
def extract_sleep_jsons_into_dataframe(data_folder: Path) -> DataFrame[RawFitbitSleep]:
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
    df = extract_json_file_data(
        data_folder, file_name_prefix="sleep", keys_to_keep=keys_to_keep
    )
    df = RawFitbitSleep.validate(df)
    return df


@pa.check_types
def transform_sleep(df: DataFrame[RawFitbitSleep]) -> DataFrame[FitbitSleep]:
    """Apply transformations to sleep dataframe, then saves dataframe in table:
    `year_in_data.fitbit_sleep_data_processed`

    Parameters
    ----------
    sleep_df : pd.DataFrame
        Raw Fibit sleep dataframe containing columns:
            `["dateOfSleep", "startTime", "endTime", "duration"]`

    """
    # Select only important data for current analysis
    df = df[
        [
            "dateOfSleep",
            "startTime",
            "endTime",
            "minutesAsleep",
        ]
    ]
    df = df.rename(
        columns={
            "dateOfSleep": "date",
            "startTime": "start_time",
            "endTime": "end_time",
            "minutesAsleep": "total_sleep_minutes",
        }
    )
    df["total_sleep_hours"] = df["total_sleep_minutes"].apply(
        lambda x: round(x / 60, 2)
    )
    df = df.drop(columns=["total_sleep_minutes"])
    df.loc[:, "start_time"] = pd.to_datetime(df["start_time"]).dt.time
    df.loc[:, "end_time"] = pd.to_datetime(df["end_time"]).dt.time
    df = (
        df.groupby(["date"])
        .aggregate(
            {
                "start_time": "first",
                "end_time": "last",
                "total_sleep_hours": "sum",
            }
        )
        .reset_index()
    )
    df["total_sleep_hours"] = df["total_sleep_hours"].round(2)
    df = FitbitSleep.validate(df)
    return df



