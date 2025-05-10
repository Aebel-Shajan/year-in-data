import pandas as pd
from yd_extractor.utils.pandas import detect_delimiter, parse_duration, validate_columns
from typing import BinaryIO
import logging
logger = logging.getLogger(__name__)

def extract_workouts(csv_file: BinaryIO):
    df_raw = pd.read_csv(
        csv_file, delimiter=detect_delimiter(csv_file), parse_dates=["Date"]
    )
    # The strong app has 2 different formats with different column names
    if "Duration" in df_raw:
        df_raw = df_raw.rename(columns={"Duration": "Workout Duration"})

    return df_raw


def transform_workouts(df: pd.DataFrame) -> pd.DataFrame:
    columns_to_keep = [
        "Date",
        "Workout Name",
        "Exercise Name",
        "Set Order",
        "Weight",
        "Reps",
        "Distance",
        "Seconds",
        "Workout Duration",
    ]
    validate_columns(df, columns_to_keep)
    # Select only columns to keep
    df = df[columns_to_keep].copy()

    # Rename everything to snake case
    rename_map = {
        "Date": "date",
        "Workout Name": "workout_name",
        "Exercise Name": "exercise_name",
        "Set Order": "set_order",
        "Weight": "weight",
        "Reps": "reps",
        "Distance": "distance",
        "Seconds": "seconds",
        "Workout Duration": "workout_duration",
    }
    df = df.rename(columns=rename_map)
    
    # Parse durations from string $h $m to milliseconds
    df["workout_duration_milliseconds"] = df["workout_duration"].apply(parse_duration)
    df.drop(columns=["workout_duration"])
    # Convert to minutes
    df["workout_duration_minutes"] = df["workout_duration_milliseconds"].apply(
        lambda x: x / (60 * 1000)
    )
    df = df.drop(columns=["workout_duration_milliseconds"])

    # Calculate volume for each workout
    df["volume"] = df["weight"] * df["reps"]

    # Set types of date and time columns
    df.loc[:, "date"] = pd.to_datetime(df["date"], format="ISO8601").dt.date
    df.loc[:, "start_time"] = pd.to_datetime(df["date"], format="ISO8601").dt.time

    # Group by for each exercise
    df = (
        df.groupby(["date", "workout_name"])
        .aggregate(
            {
                "workout_duration_minutes": "min",
                "volume": "sum",
            }
        )
        .reset_index()
    )
    df = df.rename(
        columns={
            "volume": "total_volume"
        }
    )
    df = df[
        [
            "date",
            "workout_name",
            "workout_duration_minutes",
            "total_volume"
        ]
    ]
    return df

def process_workouts(csv_file: BinaryIO) -> pd.DataFrame:
    logger.info("Processing strong workouts...")
    df_raw = extract_workouts(csv_file)
    df_transformed = transform_workouts(df_raw)
    logger.info("Finished processing strong workouts...")
    return df_transformed

