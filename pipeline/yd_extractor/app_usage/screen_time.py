import logging
from pathlib import Path
from typing import Callable, Optional

import pandas as pd
import pandera as pa
from pandera.typing.pandas import DataFrame

from yd_extractor.app_usage.app_info_map import proccess_app_info_map
from yd_extractor.app_usage.schemas import (AppInfoMap, AppUsageScreenTime,
                                            RawAppUsageScreenTime)
from yd_extractor.utils.pandas import rename_df_from_schema

logger = logging.getLogger(__name__)


@pa.check_types
def extract_screen_time(
    csv_file_path: Path,
) -> DataFrame[RawAppUsageScreenTime]:
    logger.info(f"Extracting screen time data from {csv_file_path}")
    with open(csv_file_path) as csv:
        df = pd.read_csv(csv)
    df = RawAppUsageScreenTime.validate(df)
    return df


@pa.check_types
def transform_screen_time(
    df: DataFrame[RawAppUsageScreenTime],
    df_app_info_map: Optional[DataFrame[AppInfoMap]] = None,
) -> DataFrame[AppUsageScreenTime]:
    logger.info("Transforming screen time data.")
    df = rename_df_from_schema(df, RawAppUsageScreenTime)
    df = df.dropna()
    names_to_drop = [
        "Screen on (unlocked)",
        "Screen off (locked)",
        "Device shutdown",
    ]
    df = df[~df["app_name"].isin(names_to_drop)]
    df["date"] = pd.to_datetime(df["date"], format="%m/%d/%y")
    df["duration_minutes"] = pd.to_timedelta(df["duration"]).dt.total_seconds() / 60
    df["duration_minutes"] = df["duration_minutes"].round().astype(int)
    df = df[df["duration_minutes"] > 0]
    df = df.drop(columns=["duration"])

    if df_app_info_map is not None:
        df = pd.merge(
            df,
            df_app_info_map,
            how="left",
        )
        df["image"] = df["image"].fillna("")
        df["category"] = df["category"].fillna("")
    df = AppUsageScreenTime.validate(df)
    return df


def process_screen_time(
    csv_file_path: Path,
    app_info_path: Optional[Path] = None,
    load_function: Optional[Callable[[pd.DataFrame, str], None]] = None,
) -> DataFrame[AppUsageScreenTime]:
    df = AppUsageScreenTime.empty()
    try:
        df = extract_screen_time(csv_file_path)
        df_app_info_map = None
        if app_info_path:
            df_app_info_map = proccess_app_info_map(app_info_path)
        df = transform_screen_time(df, df_app_info_map)
        if load_function:
            load_function(df, "app_usage_screen_time")
    except Exception:
        logger.exception("Error whilst processing screen time.")
    return df


if __name__ == "__main__":
    csv_file_path = "data/input/AUM_V4_Activity_2025-05-10_21-56-06.csv"
    app_info_path = "data/input/AUM_V4_App_2025-05-14_14-53-26.csv"
    logger = logging.getLogger()
    logging.basicConfig(level=logging.INFO)

    def load_to_csv(df: pd.DataFrame, name: str):
        df.to_csv("data/output/" + name + ".csv", index=False)

    process_screen_time(
        csv_file_path, app_info_path=app_info_path, load_function=load_to_csv
    )
