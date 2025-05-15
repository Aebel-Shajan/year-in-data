import logging
from typing import BinaryIO, Callable, Optional

import pandas as pd
import pandera as pa
from pandera.typing.pandas import DataFrame

from yd_extractor.utils.pipeline_stage import PipelineStage
from yd_extractor.strong.schemas import RawStrongWorkouts, StrongWorkouts
from yd_extractor.utils.pandas import detect_delimiter, rename_df_from_schema

logger = logging.getLogger(__name__)


@pa.check_types()
def extract_workouts(csv_path: str) -> DataFrame[RawStrongWorkouts]:
    with open(csv_path) as csv_file:
        df_raw = pd.read_csv(
            csv_file,
            delimiter=detect_delimiter(csv_file),
            parse_dates=["Date"],
        )
    RawStrongWorkouts.validate(df_raw)
    return df_raw


@pa.check_types
def transform_workouts(df: DataFrame[RawStrongWorkouts]) -> DataFrame[StrongWorkouts]:

    if "Weight (lb)" in df.columns:
        df["Weight (kg)"] = df["Weight (lb)"] * 0.453592
        df = df.drop("Weight (lb)", axis=1)

    if "Distance (miles)" in df.columns:
        df["Distance (km)"] = df["Distance (miles)"] * 1.60934
        df = df.drop("Distance (miles)", axis=1)

    df = rename_df_from_schema(df, RawStrongWorkouts)

    # Convert to minutes
    df["workout_duration_minutes"] = df["workout_duration_seconds"] / 60
    df["workout_duration_minutes"] = df["workout_duration_minutes"].astype(int)
    df = df.drop("workout_duration_seconds", axis=1)

    # Calculate volume for each exercise
    df["volume"] = df["weight"] * df["reps"]

    # Set types of date and time columns
    df.loc[:, "start_time"] = df["date"].dt.time
    df.loc[:, "date"] = df["date"].dt.date
    df["workout_name"] = pd.Categorical(df["workout_name"])

    # Group Workouts together
    df = (
        df.groupby("workout_number")
        .aggregate(
            {
                "date": "first",
                "start_time": "first",
                "workout_name": "first",
                "workout_duration_minutes": "first",
                "volume": "sum",
            }
        )
        .reset_index()
    )
    df = df.rename(columns={"volume": "workout_volume"})
    df["workout_volume"] = df["workout_volume"].astype(int)
    df = df[
        [
            "workout_number",
            "date",
            "start_time",
            "workout_name",
            "workout_duration_minutes",
            "workout_volume",
        ]
    ]
    StrongWorkouts.validate(df)
    return df


def process_workouts(
    csv_path: str,
    load_function: Optional[Callable[[pd.DataFrame, str], None]] = None,    
) -> pd.DataFrame:
    with PipelineStage(logger, "strong_workouts"):
        df = extract_workouts(csv_path)
        df = transform_workouts(df)
        if load_function:
            load_function(df, "strong_workouts", StrongWorkouts)
    return df

