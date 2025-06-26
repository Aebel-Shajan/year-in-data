import dagster as dg
from orchestrator.assets.common_assets import landing_zone
from transformations.utils.io import get_latest_valid_csv
from transformations.strong.schemas import RawStrongWorkouts
from transformations.strong import workouts
import pandas as pd



@dg.asset(
    deps=[landing_zone],
    kinds={"bronze"},
)
def latest_strong_csv(landing_zone: str) -> str:
    strong_folder = landing_zone + "/strong"
    csv_path = get_latest_valid_csv(
        folder_path=strong_folder,
        file_name_glob="*.csv",
        expected_schema=RawStrongWorkouts,
        expected_delimiter=";",
    )
    return csv_path

@dg.asset(
    deps=[latest_strong_csv],
    kinds={"silver"}
)
def strong_workouts_raw(latest_strong_csv: str) -> pd.DataFrame:
    df = workouts.extract_workouts(latest_strong_csv)
    return df


@dg.asset(
    deps=[strong_workouts_raw],
    kinds={"gold"},
)
def strong_workouts(strong_workouts_raw: pd.DataFrame) -> pd.DataFrame:
    df = workouts.transform_workouts(strong_workouts_raw)
    return df