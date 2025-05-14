from pathlib import Path
from pandera.typing.pandas import DataFrame
from yd_extractor.app_usage.schemas import RawAppUsageScreenTime, AppUsageScreenTime
from yd_extractor.utils.pandas import rename_df_from_schema
import pandas as pd
import pandera as pa
from typing import Callable


@pa.check_types
def extract_screen_time(
    csv_file_path: Path,
) -> DataFrame[RawAppUsageScreenTime]:
    with open(csv_file_path) as csv:
        df = pd.read_csv(csv)
    df = RawAppUsageScreenTime.validate(df)
    return df


@pa.check_types
def transform_screen_time(
    df: DataFrame[RawAppUsageScreenTime],
) -> DataFrame[AppUsageScreenTime]:
    df = rename_df_from_schema(df, RawAppUsageScreenTime)
    df = df.dropna()
    names_to_drop = [
        "Screen on (unlocked)",
        "Screen off (locked)",
        "Device shutdown",
    ]
    df = df[~df["app_name"].isin(names_to_drop)]
    df["date"] = pd.to_datetime(df["date"], format="%m/%d/%y")
    df['duration_minutes'] = pd.to_timedelta(df["duration"]).dt.total_seconds() / 60
    df["duration_minutes"] = df["duration_minutes"].round().astype(int)
    df = df[df["duration_minutes"] > 0]
    df = df.drop(columns=["duration"])
    df = AppUsageScreenTime.validate(df)
    return df


def process_screen_time(
    csv_file_path: Path,
    load_function: Callable[[pd.DataFrame, str], None] = lambda x, y: None,
) -> DataFrame[AppUsageScreenTime]:
    df = extract_screen_time(csv_file_path)
    df = transform_screen_time(df)
    load_function(df, "app_usage_screen_time")
    return df




if __name__ == "__main__":
    csv_file_path = "data/input/AUM_V4_Activity_2025-05-10_21-56-06.csv"
    def load_to_csv(df: pd.DataFrame, name: str):
        df.to_csv("data/output/"+name + ".csv", index=False)
    process_screen_time(csv_file_path, load_to_csv)
    