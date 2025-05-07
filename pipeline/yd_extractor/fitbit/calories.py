from pathlib import Path
import shutil
import pandas as pd

from yd_extractor.utils.utils import extract_specific_files_flat

from .utils import extract_json_file_data, transform_time_series_data
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def process_calories(
    inputs_folder: Path,
    zip_path: Path,
    cleanup: bool=True
) -> pd.DataFrame:
    """Extract calories from folder then apply some transformations on data."""
    
    # Unzip and extract calories jsons from zip file.
    logger.info("extracting files for calories...")
    data_folder = inputs_folder / "calories"
    extract_specific_files_flat(
        zip_file_path=zip_path,
        prefix="Takeout/Fitbit/Global Export Data/calories",
        output_path=data_folder
    )
    logger.info("extracting data from calories json files...")
    df_raw = extract_json_file_data(
        folder_path=data_folder,
        file_name_prefix="calories",
        keys_to_keep=["dateTime", "value"]
    )
    logger.info("transforming extracted data...")
    df_transformed = transform_time_series_data(df=df_raw)
    
    if cleanup:
        logger.info("Removing extracted data from zip...")
        shutil.rmtree(data_folder)
        
    return df_transformed