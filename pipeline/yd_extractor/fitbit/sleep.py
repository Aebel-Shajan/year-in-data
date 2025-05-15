import logging
import shutil
from pathlib import Path
from typing import Callable, Optional

import pandas as pd
import pandera as pa
from pandera.typing.pandas import DataFrame

from yd_extractor.utils.pipeline_stage import PipelineStage
from yd_extractor.fitbit.schemas import FitbitSleep, RawFitbitSleep
from yd_extractor.fitbit.utils import extract_json_file_data
from yd_extractor.utils.utils import extract_specific_files_flat

logger = logging.getLogger(__name__)


@pa.check_types
def extract_sleep(data_folder: Path, zip_path: Path) -> DataFrame[RawFitbitSleep]:
    """Extract sleep data from files from the folder path. The files have the name format
    "sleep-YYYY-MM-DD.json".

    Parameters
    ----------
    folder_path : str
        Path to folder containing jsons with sleep data.
    """
    extract_specific_files_flat(
        zip_file_path=zip_path,
        prefix="Takeout/Fitbit/Global Export Data/sleep",
        output_path=data_folder,
    )
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


def process_sleep(
    inputs_folder: Path,
    zip_path: Path,
    load_function: Optional[Callable[[pd.DataFrame, str], None]] = None,
    cleanup: bool = True,
) -> pd.DataFrame:
    # Unzip and extract calories jsons from zip file.
    df = FitbitSleep.empty()
    data_folder = inputs_folder / "sleep"
    
    with PipelineStage(logger, "fitbit_sleep"):
        df = extract_sleep(data_folder, zip_path)
        df = transform_sleep(df)
        if load_function:
            load_function(df, "fitbit_sleep")

    if cleanup:
        logger.info(f"Removing folder {data_folder} from zip...")
        shutil.rmtree(data_folder)

    return df
