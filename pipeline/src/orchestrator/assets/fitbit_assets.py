from pathlib import Path
import dagster as dg
import pandas as pd
from transformations.utils.io import get_latest_valid_zip
from transformations.fitbit import calories
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
def raw_fitbit_calories(fitbit_calories_jsons: str) -> pd.DataFrame:
    df = calories.extract_calories_jsons_into_dataframe(fitbit_calories_jsons)
    return df


@dg.asset(
    deps=[raw_fitbit_calories],
    kinds={"gold"},
)
def fitbit_calories(raw_fitbit_calories: pd.DataFrame) -> pd.DataFrame:
    df = calories.transform_calories(raw_fitbit_calories)
    return df
