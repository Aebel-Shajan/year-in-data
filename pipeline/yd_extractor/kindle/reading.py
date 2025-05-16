import logging
import shutil
from pathlib import Path
from typing import Callable, Optional, Union

import pandas as pd
import pandera as pa
from pandera.typing.pandas import DataFrame

from yd_extractor.utils.pipeline_stage import PipelineStage
from yd_extractor.kindle.asin_map import process_asin_map
from yd_extractor.kindle.schemas import (AsinMap, KindleReading,
                                         RawKindleReading)
from yd_extractor.utils.pandas import detect_delimiter, rename_df_from_schema
from yd_extractor.utils.utils import extract_specific_files_flat

logger = logging.getLogger(__name__)


@pa.check_types
def extract_reading(data_folder: Path, zip_file_path) -> DataFrame[RawKindleReading]:
    kindle_search_prefix = (
        "Kindle.Devices.ReadingSession" "/Kindle.Devices.ReadingSession.csv"
    )
    extract_specific_files_flat(
        zip_file_path=zip_file_path,
        prefix=kindle_search_prefix,
        output_path=data_folder,
    )
    csv_path = data_folder / "Kindle.Devices.ReadingSession.csv"
    # Read in csv from config into a pandas dataframe
    df = None
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


def process_reading(
    inputs_folder: Path,
    zip_path: Path,
    cleanup: bool = True,
    load_function: Optional[Callable[[pd.DataFrame, str], None]] = None,
) -> pd.DataFrame:
    """
    Read in kindle data from csv file.

    """
    df = KindleReading.empty()
    
    with PipelineStage(logger, "kindle_reading"):
        data_folder = inputs_folder / "kindle"
        df = extract_reading(data_folder, zip_path)
        asin_map = process_asin_map(inputs_folder, zip_path, cleanup)
        df = transform_reading(df, asin_map)
        if load_function:
            load_function(df, "kindle_reading", KindleReading)
        
    if cleanup:
        logger.info(f"Removing folder {data_folder} from zip...")
        shutil.rmtree(data_folder)
        
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


if __name__ == "__main__":
    df = process_reading(
        inputs_folder=Path("data/input"),
        zip_path=Path("data/input/Kindle.zip"),
    )
    # breakpoint()
    # df.to_csv(Path("data/output/kindle_reading.csv"), index=False)
