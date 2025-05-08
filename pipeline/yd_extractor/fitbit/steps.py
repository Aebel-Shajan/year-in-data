from pathlib import Path
import shutil
import pandas as pd

from yd_extractor.utils.utils import extract_specific_files_flat

from .utils import extract_json_file_data, transform_time_series_data


def process_steps(
    inputs_folder: Path,
    zip_path: Path,
    cleanup: bool=True
) -> pd.DataFrame:

    # Unzip and extract calories jsons from zip file.
    data_folder = inputs_folder / "steps"
    extract_specific_files_flat(
        zip_file_path=zip_path,
        prefix="Takeout/Fitbit/Global Export Data/steps",
        output_path=data_folder
    )
    df_raw = extract_json_file_data(
        folder_path=data_folder,
        file_name_prefix="steps",
        keys_to_keep=["dateTime", "value"]
    )
    df_transformed = transform_time_series_data(df_raw)
    
    if cleanup:
        shutil.rmtree(data_folder)
    
    return df_transformed
