import logging
import shutil
from pathlib import Path

import pandas as pd

from yd_extractor.fitbit.utils import (extract_json_file_data,
                                       transform_time_series_data)
from yd_extractor.utils.utils import extract_specific_files_flat

logger = logging.getLogger(__name__)


def process_steps(
    inputs_folder: Path, zip_path: Path, cleanup: bool = True
) -> pd.DataFrame:

    # Unzip and extract calories jsons from zip file.
    logger.info("Processing fitbit steps...")

    data_folder = inputs_folder / "steps"
    extract_specific_files_flat(
        zip_file_path=zip_path,
        prefix="Takeout/Fitbit/Global Export Data/steps",
        output_path=data_folder,
    )
    df_raw = extract_json_file_data(
        folder_path=data_folder,
        file_name_prefix="steps",
        keys_to_keep=["dateTime", "value"],
    )
    df_transformed = transform_time_series_data(df_raw)

    logger.info("Finished processing fitbit steps")

    if cleanup:
        shutil.rmtree(data_folder)

    return df_transformed
