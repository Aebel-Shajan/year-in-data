from pathlib import Path
import dagster as dg
import pandas as pd
from transformations.kindle import reading, asin_map
from transformations.utils.io import get_latest_valid_zip
from orchestrator.assets.common_assets import landing_zone


@dg.asset(
    deps=[landing_zone],
    kinds={"bronze"},
)
def kindle_zip(landing_zone: str) -> str:
    zip_file = get_latest_valid_zip(
        folder_path=Path(landing_zone + "/amazon"),
        file_name_glob="*.zip",
        expected_file_path="Kindle.Devices.ReadingSession"
    )
    if zip_file:
        return str(zip_file)
    else:
        raise dg.Failure(
            description="No valid amazon zip found which contains kindle data."
        )
        
    

# Reading
@dg.asset(
    deps=[kindle_zip],
    kinds={"bronze"},
)
def kindle_reading_csv(kindle_zip: str) -> str:
    output_dir = "data/bronze/stage/kindle"
    csv_path = reading.extract_reading_csv(kindle_zip, output_dir)
    return csv_path


@dg.asset(
    deps=[kindle_reading_csv],
    kinds={"silver"},
)
def kindle_reading_raw(kindle_reading_csv: str) -> pd.DataFrame:
    df = reading.extract_reading_csv_into_df(kindle_reading_csv)
    return df

# Asin map
@dg.asset(
    deps=[kindle_zip],
    kinds={"bronze"},
)
def kindle_digital_content_jsons(kindle_zip: str) -> str:
    output_folder = "data/bronze/stage/kindle/digital_content_jsons"
    asin_map.extract_digital_content_jsons(kindle_zip, output_folder)
    return output_folder


@dg.asset(
    deps=[kindle_digital_content_jsons],
    kinds={"silver"},
)
def kindle_asin_map_raw(kindle_digital_content_jsons: str) -> pd.DataFrame:
    df = asin_map.extract_asin_map(kindle_digital_content_jsons)
    return df

@dg.asset(
    deps=[kindle_asin_map_raw],
    kinds={"silver"}
)
def kindle_asin_map(kindle_asin_map_raw: pd.DataFrame) -> pd.DataFrame:
    df = asin_map.transform_asin_map(kindle_asin_map_raw)
    return df
    
# Derived
@dg.asset(
    deps=[kindle_reading_raw, kindle_asin_map],
    kinds={"gold"}
)
def kindle_reading(
    kindle_reading_raw: pd.DataFrame, 
    kindle_asin_map: pd.DataFrame,
) -> pd.DataFrame:
    df = reading.transform_reading(kindle_reading_raw, kindle_asin_map)
    return df
