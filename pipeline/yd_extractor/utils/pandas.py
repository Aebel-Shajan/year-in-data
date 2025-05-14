import csv
import logging
import re
from typing import BinaryIO

import pandas as pd
import pandera as pa

logger = logging.getLogger(__name__)


def detect_delimiter(csv_file: BinaryIO) -> str:
    """
    Detect the delimiter used in a CSV file.

    Parameters
    ----------
    csv_file : BinaryIO
        The path to the CSV file.

    Returns
    -------
    str
        The detected delimiter (e.g. ',', ';', '\t', etc.).
    """
    delimeter = ","
    try:
        original_pos = csv_file.tell()
        content = csv_file.read(1024)
        if type(content) != str:
            content = content.decode("utf-8")
        csv_file.seek(original_pos)
        dialect = csv.Sniffer().sniff(content)
        delimeter = dialect.delimiter
    except:
        delimeter = ","
    return delimeter


def check_columns_exist(df: pd.DataFrame, columns: list[str]) -> bool:
    """Checks if a given dataframe contains the provided columns.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe to check columns.
    columns : list[str]
        Columns to check.

    Returns
    -------
    bool
        True if dataframe contains all columns provided. False otherwise.
    """
    return set(columns).issubset(df.columns)


def validate_columns(df: pd.DataFrame, columns_to_validate: list[str]) -> None:
    if not set(df.columns).issubset(df.columns):
        raise ValueError(
            "df provided does not contain required columns!\n"
            f"\t* df columns: {list(df.columns)}\n"
            f"\t* Required columns: {columns_to_validate}"
        )


def parse_duration(duration: str) -> float:
    """Convert duration from the format `{hours}h {minutes}m` to milliseconds

    Parameters
    ----------
    duration : str
        Duration string in one of the formats:
            * `{hours}h {minutes}m`
            * `{hours}h`
            * `{minutes}m`

    Returns
    -------
    duration_ms : float
        Duration in milliseconds
    """

    def throw_error():
        raise ValueError("duration must have type like `{hours}h {minutes}m`")

    duration_ms = 0
    parts = duration.split()
    # Validation
    if len(parts) > 2 or len(parts) == 0:
        throw_error()
    for part in parts:
        if not part[:-1].isnumeric():
            throw_error()
        if not (part.endswith("h") or part.endswith("m")):
            throw_error()

    for index, part in enumerate(parts):
        if part.endswith("h") and index == 0:
            hours = part.rstrip("h")
            duration_ms += float(hours) * 60 * 60 * 1000
        elif part.endswith("m"):
            minutes = part.rstrip("m")
            duration_ms += float(minutes) * 60 * 1000

    return duration_ms


def convert_columns_to_numeric(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    validate_columns(df, columns_to_validate=columns)
    for column in columns:
        df.loc[:, column] = pd.to_numeric(df[column])

    return df


def rename_df_from_schema(df: pd.DataFrame, schema: pa.DataFrameModel) -> pd.DataFrame:
    """Rename Dataframe from alias defined in schema to schema attribute

    Parameters
    ----------
        df (pd.DataFrame): Pandas dataframe which has been validated by schema.
        schema (pa.DataFrameModel): Pandera schema which have fields with aliases.

    Returns
    -------
        pd.DataFrame: Dataframe with names which match the attributes found in the
            schema.
    """
    rename_fields = {}

    for key, value in schema._collect_fields().items():
        current_name = key
        new_name = value[1].original_name
        if value[1].regex:
            matching_columns = [
                col for col in df.columns if re.match(current_name, col)
            ]
            if len(matching_columns) == 1:
                current_name = matching_columns[0]
            else:
                logger.warning(
                    f"Multiple/Zero columns ({matching_columns}) match the regex "
                    f"'{current_name}' for field '{new_name}' in schema "
                    f"{schema.__class__.__name__}."
                )
        rename_fields[current_name] = new_name

    return df.rename(columns=rename_fields)
