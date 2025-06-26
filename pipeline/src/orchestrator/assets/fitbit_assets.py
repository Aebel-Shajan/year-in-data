from pathlib import Path
import dagster as dg
import pandas as pd
from transformations.utils.io import extract_specific_files_flat, get_latest_valid_zip
from transformations.fitbit import calories, common, exercise, sleep
from orchestrator.assets.common_assets import landing_zone


@dg.asset(
    deps=[landing_zone],
    kinds={"bronze"},
)
def fitbit_zip(landing_zone: str) -> str:
    zip_file = get_latest_valid_zip(
        folder_path=Path(landing_zone + "/google"),
        file_name_glob="*.zip",
        expected_file_path="Takeout/Fitbit/Global Export Data",
    )
    if zip_file:
        return str(zip_file)
    else:
        raise dg.Failure(
            description="No valid google takeout zip found which contains fitbit data."
        )

# Calories
@dg.asset(
    deps=[fitbit_zip],
    kinds={"bronze"},
)
def fitbit_calories_jsons(fitbit_zip: str) -> str:
    output_folder = "data/bronze/stage/fitbit/calories"
    return calories.extract_calories_jsons(fitbit_zip, output_folder)


@dg.asset(
    deps=[fitbit_calories_jsons],
    kinds={"silver"},
)
def fitbit_calories_raw(fitbit_calories_jsons: str) -> pd.DataFrame:
    df = calories.extract_calories_jsons_into_dataframe(fitbit_calories_jsons)
    return df


@dg.asset(
    deps=[fitbit_calories_raw],
    kinds={"gold"},
)
def fitbit_calories(fitbit_calories_raw: pd.DataFrame) -> pd.DataFrame:
    df = calories.transform_calories(fitbit_calories_raw)
    return df


# Exercise
@dg.asset(
    deps=[fitbit_zip],
    kinds={"bronze"},
)
def fitbit_exercise_jsons(fitbit_zip: str) -> str:
    output_folder = "data/bronze/stage/fitbit/exercise"
    json_folder_path = exercise.extract_exercise_jsons(
        data_folder=output_folder,
        zip_path=fitbit_zip,
    )
    return json_folder_path


@dg.asset(
    deps=[fitbit_exercise_jsons],
    kinds={"silver"},
)
def fitbit_exercise_raw(fitbit_exercise_jsons: str) -> pd.DataFrame:
    df = exercise.extract_exercise_jsons_into_dataframe(fitbit_exercise_jsons)
    return df


@dg.asset(
    deps=[fitbit_exercise_raw],
    kinds={"gold"}
)
def fitbit_exercise(fitbit_exercise_raw: pd.DataFrame) -> pd.DataFrame:
    df = exercise.transform_exercise(fitbit_exercise_raw)
    return df


# Sleep
@dg.asset(
    deps=[fitbit_zip],
    kinds={"bronze"},
)
def fitbit_sleep_jsons(fitbit_zip: str) -> str:
    output_folder = "data/bronze/stage/fitbit/sleep"
    json_folder_path = sleep.extract_sleep_jsons(
        output_folder=output_folder,
        zip_path=fitbit_zip,
    )
    return json_folder_path


@dg.asset(
    deps=[fitbit_sleep_jsons],
    kinds={"silver"},
)
def fitbit_sleep_raw(fitbit_sleep_jsons: str) -> pd.DataFrame:
    df = sleep.extract_sleep_jsons_into_dataframe(fitbit_sleep_jsons)
    return df


@dg.asset(
    deps=[fitbit_sleep_raw],
    kinds={"gold"}
)
def fitbit_sleep(fitbit_sleep_raw: pd.DataFrame) -> pd.DataFrame:
    df = sleep.transform_sleep(fitbit_sleep_raw)
    return df


# Steps 
@dg.asset(
    deps=[fitbit_zip],
    kinds={"bronze"},
)
def fitbit_steps_jsons(fitbit_zip: str) -> str:
    output_folder = "data/bronze/stage/fitbit/steps"
    extract_specific_files_flat(
        zip_file_path=fitbit_zip,
        prefix="Takeout/Fitbit/Global Export Data/steps",
        output_path=output_folder,
    )
    return output_folder


@dg.asset(
    deps=[fitbit_steps_jsons],
    kinds={"silver"},
)
def fitbit_steps_raw(fitbit_steps_jsons: str) -> pd.DataFrame:
    df = common.extract_json_file_data(
        folder_path=fitbit_steps_jsons,
        file_name_prefix="steps",
        keys_to_keep=["dateTime", "value"],
    )
    return df
    
@dg.asset(
    deps=[fitbit_steps_raw],
    kinds={"gold"},
)
def fitbit_steps(fitbit_steps_raw: pd.DataFrame) -> pd.DataFrame:
    df = common.transform_time_series_data(fitbit_steps_raw)
    return df
