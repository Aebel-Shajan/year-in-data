import logging
import pandas as pd

from transformations.fitbit.common import (
    extract_json_file_data,
    transform_time_series_data,
)
from transformations.utils.io import extract_specific_files_flat
from transformations.fitbit.schemas import FitbitCalories, RawTimeSeriesData


logger = logging.getLogger(__name__)


def extract_calories_jsons(fitbit_zip_path: str, output_folder: str) -> str:
    extract_specific_files_flat(
        zip_file_path=fitbit_zip_path,
        prefix="Takeout/Fitbit/Global Export Data/calories",
        output_path=output_folder,
    )
    return output_folder

def extract_calories_jsons_into_dataframe(json_file_path: str) -> pd.DataFrame:
    df = extract_json_file_data(
        folder_path=json_file_path,
        file_name_prefix="calories",
        keys_to_keep=["dateTime", "value"],
    )
    df = RawTimeSeriesData.validate(df)
    return df

def transform_calories(df: pd.DataFrame) -> pd.DataFrame:
    df = transform_time_series_data(df)
    df = FitbitCalories.validate(df)
    return df 