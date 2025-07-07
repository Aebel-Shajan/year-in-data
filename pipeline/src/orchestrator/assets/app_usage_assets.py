from orchestrator.assets.common_assets import landing_zone
import dagster as dg
import pandas as pd
from transformations.utils.io import get_latest_valid_csv
from schemas import app_usage_schemas
from transformations.app_usage import screen_time, app_info_map
from dagster_pandera import pandera_schema_to_dagster_type



# Screen time
@dg.asset(
    deps=[landing_zone],
    kinds={"bronze"},
)
def latest_app_usage_activity_csv(landing_zone: str) -> str:
    app_usage_folder = landing_zone + "/app_usage"
    latest_app_usage_activity_csv = get_latest_valid_csv(
        folder_path=app_usage_folder,
        file_name_glob="*.csv",
        expected_schema=app_usage_schemas.RawAppUsageScreenTime,
        expected_delimiter=",",
    )
    return latest_app_usage_activity_csv
    

@dg.asset(
    deps=[latest_app_usage_activity_csv],
    kinds={"silver"},
    dagster_type=pandera_schema_to_dagster_type(app_usage_schemas.RawAppUsageScreenTime),
)
def app_usage_screen_time_raw(latest_app_usage_activity_csv: str) -> pd.DataFrame:
    df = screen_time.extract_screen_time(latest_app_usage_activity_csv)
    return df


# App info
@dg.asset(
    deps=[landing_zone],
    kinds={"bronze"},
)
def latest_app_usage_app_csv(landing_zone: str) -> str:
    app_usage_folder = landing_zone + "/app_usage"
    csv_path = get_latest_valid_csv(
        folder_path=app_usage_folder,
        file_name_glob="*.csv",
        expected_schema=app_usage_schemas.RawAppUsageAppInfo,
        expected_delimiter=",",
    )
    return csv_path


@dg.asset(
    deps=[latest_app_usage_app_csv],
    kinds={"silver"},
    dagster_type=pandera_schema_to_dagster_type(app_usage_schemas.RawAppUsageAppInfo),
)
def app_usage_app_info_raw(latest_app_usage_app_csv: str) -> pd.DataFrame:
    df = app_info_map.extract_app_info_map(latest_app_usage_app_csv)
    return df


@dg.asset(
    deps=[app_usage_app_info_raw],
    kinds={"silver"},
    dagster_type=pandera_schema_to_dagster_type(app_usage_schemas.AppUsageAppInfo),
)
def app_usage_app_info(app_usage_app_info_raw: pd.DataFrame) -> pd.DataFrame:
    df = app_info_map.transform_app_info_map(app_usage_app_info_raw)
    return df


@dg.asset(
    deps=[app_usage_app_info, app_usage_screen_time_raw],
    kinds={"gold"},
    dagster_type=pandera_schema_to_dagster_type(app_usage_schemas.AppUsageScreenTime),
)
def app_usage_screen_time(
    app_usage_app_info: pd.DataFrame, 
    app_usage_screen_time_raw: pd.DataFrame
) -> pd.DataFrame:
    df = screen_time.transform_screen_time(app_usage_screen_time_raw, app_usage_app_info)
    return df
