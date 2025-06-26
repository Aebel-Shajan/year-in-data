import logging
from typing import Union

import pandas as pd
import pandera as pa
from pandera.typing.pandas import DataFrame

from transformations.kindle.schemas import (AsinMap, KindleReading,
                                         RawKindleReading)
from transformations.utils.pandas import detect_delimiter, rename_df_from_schema
from transformations.utils.io import extract_specific_files_flat

logger = logging.getLogger(__name__)


def extract_reading_csv(zip_path: str, output_path: str) -> str:
    kindle_search_prefix = (
        "Kindle.Devices.ReadingSession" "/Kindle.Devices.ReadingSession.csv"
    )
    extract_specific_files_flat(
        zip_file_path=zip_path,
        prefix=kindle_search_prefix,
        output_path=output_path,
    )
    csv_path = output_path + "/" + "Kindle.Devices.ReadingSession.csv"
    return csv_path


@pa.check_types
def extract_reading_csv_into_df(csv_path: str) -> DataFrame[RawKindleReading]:
    # Read in csv from config into a pandas dataframe
    with open(csv_path) as csv_file:
        delimeter = detect_delimiter(csv_file)
        df = pd.read_csv(
            csv_file,
            delimiter=delimeter,
            parse_dates=["start_timestamp", "end_timestamp"],
        )
        df = RawKindleReading.validate(df)
        return df


def transform_reading(
    df: DataFrame[RawKindleReading],
    asin_map: DataFrame[AsinMap],
) -> DataFrame[KindleReading]:
    df = rename_df_from_schema(df, RawKindleReading)
    df = df[df["start_timestamp"] != "Not Available"]
    df["start_timestamp"] = pd.to_datetime(df["start_timestamp"])
    df.loc[:, "date"] = df["start_timestamp"].dt.date
    df.loc[:, "start_time"] = df["start_timestamp"].dt.time
    df["total_reading_minutes"] = df["total_reading_millis"].apply(
        lambda x: round(x / (60 * 1000))
    )
    df.drop("total_reading_millis", axis=1)
    df = (
        df.groupby(["asin", "date"])
        .aggregate(
            {
                "start_time": "min",
                "total_reading_minutes": "sum",
                "number_of_page_flips": "sum",
            }
        )
        .reset_index()
    )

    # Inner join on asin map
    df = asin_map.merge(df, how="inner", on="asin")
    df = df.rename(columns={"product_name": "book_name"})
    df["image"] = df["asin"].apply(get_asin_image)

    df = df[
        [
            "date",
            "start_time",
            "asin",
            "book_name",
            "total_reading_minutes",
            "image",
            "number_of_page_flips",
        ]
    ]
    df = KindleReading.validate(df)
    return df


def is_valid_asin(asin: str) -> bool:
    """Checks if a given string is an ASIN code. Asin codes are made of 10 alphanumeric
    characters. They begin with "B0"

    Parameters
    ----------
    asin : str
        String to check

    Returns
    -------
    bool
        True if input is an asin code.
    """
    return (
        len(asin) == 10 and asin.isalnum() and asin.isupper() and asin.startswith("B0")
    )


def get_asin_image(asin: str) -> Union[str, None]:
    """Returns the image url associated with a given asin code. Returns None if not valid
    asin.

    Parameters
    ----------
    asin : str
        asin code.

    Returns
    -------
    str | None
        Returns asin image url if input is valid asin code. Otherwise returns None.
    """
    if not is_valid_asin(asin):
        return None
    return f"https://images.amazon.com/images/P/{asin}.jpg"
