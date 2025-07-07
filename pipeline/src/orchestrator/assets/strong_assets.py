import dagster as dg
from orchestrator.assets.common_assets import landing_zone
from transformations.utils.io import get_latest_valid_csv
from schemas import strong_schemas
from transformations.strong import workouts
import pandas as pd
from dagster_pandera import pandera_schema_to_dagster_type



@dg.asset(
    deps=[landing_zone],
    kinds={"bronze"},
)
def latest_strong_csv(landing_zone: str) -> str:
    strong_folder = landing_zone + "/strong"
    csv_path = get_latest_valid_csv(
        folder_path=strong_folder,
        file_name_glob="*.csv",
        expected_schema=strong_schemas.RawStrongWorkouts,
        expected_delimiter=";",
    )
    return csv_path

@dg.asset(
    deps=[latest_strong_csv],
    kinds={"silver"},
    dagster_type=pandera_schema_to_dagster_type(strong_schemas.RawStrongWorkouts),
)
def strong_workouts_raw(latest_strong_csv: str) -> pd.DataFrame:
    df = workouts.extract_workouts(latest_strong_csv)
    return df


@dg.asset(
    deps=[strong_workouts_raw],
    kinds={"gold"},
    dagster_type=pandera_schema_to_dagster_type(strong_schemas.StrongWorkouts),
)
def strong_workouts(strong_workouts_raw: pd.DataFrame) -> pd.DataFrame:
    df = workouts.transform_workouts(strong_workouts_raw)
    return df