import json
import os

import pandas as pd
import psutil
import logging
from yd_extractor.utils.pandas import validate_columns
logger = logging.getLogger(__name__)


def extract_json_file_data(folder_path: str, file_name_prefix: str, keys_to_keep: list[str]) -> pd.DataFrame:
    """Extract fitbit data from the folder path containing jsons. The files in the folder
    have the format like : "{file_name_prefix}-YYYY-MM-DD.json".

    Parameters
    ----------
    folder_path : str
        Path to folder containing jsons of fitbit data.
    file_name_prefix : str
        Defines what specific data to filter.
    keys_to_keep : list[str]
        From the jsons, keys_to_keep determines which key value pairs should be kept.

    Returns
    -------
    pd.DataFrame
        Pandas dataframe with keys_to_keep as the columns with rows being objects/dicts 
        extracted from the jsons.
    """
    file_names = [f for f in os.listdir(folder_path) if f.startswith(file_name_prefix)]
    if len(file_names) == 0:
        raise Exception(f"No files found with prefix: {file_name_prefix}")
    full_data = []
    for file_name in file_names:
        file_path = folder_path / file_name
        with open(file_path) as file:
            data_list = json.load(file)
            for data in data_list:
                filtered_data = {key: data[key] for key in keys_to_keep if key in list(data.keys())}
                if filtered_data.keys() != keys_to_keep:
                    full_data.append(filtered_data)
            

    return pd.DataFrame(full_data)

def transform_time_series_data(df: pd.DataFrame) -> pd.DataFrame:
    """Apply transformations to dataframe containing timeseries data.

    Parameters
    ----------
    df : pd.DataFrame
        dataframe containing columns:
        * dateTime with type string.
        * value with type integer.
        
    Returns
    -------
    pd.DataFrame
        Dataframe containing columns:
        * date with type datetime.
        * value with type integer.
    """
    columns_to_keep = ["dateTime", "value"]
    validate_columns(df, columns_to_keep)
    df = df[columns_to_keep]
    df = df.rename(
        columns={
            "dateTime": "date",
        }
    )
    df.loc[:, "value"] = pd.to_numeric(df["value"])
    df.loc[:, "date"] = pd.to_datetime(df["date"], format="%m/%d/%y %H:%M:%S").dt.date
    df = df.groupby(["date"]).aggregate(
        {
            "value": "sum",
        }
    ).reset_index()
    df["value"] = df["value"].astype(int)
    return df
