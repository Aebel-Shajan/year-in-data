import logging
import shutil
from pathlib import Path
from typing import Callable, Optional

import pandas as pd

from yd_extractor.utils.pipeline_stage import PipelineStage
from yd_extractor.fitbit.utils import (extract_json_file_data,
                                       transform_time_series_data)
from yd_extractor.utils.logger import (log_system_resources,
                                       redirect_output_to_logger)
from yd_extractor.utils.io import extract_specific_files_flat
from yd_extractor.fitbit.schemas import TimeSeriesData

logger = logging.getLogger(__name__)


def process_calories(
    inputs_folder: Path, 
    zip_path: Path, 
    cleanup: bool = True,
    load_function: Optional[Callable[[pd.DataFrame, str], None]] = None,
) -> pd.DataFrame:
    """Extract calories from folder then apply some transformations on data."""
    # Unzip and extract calories jsons from zip file.
    df = TimeSeriesData.empty()
    data_folder = inputs_folder / "calories"
    with PipelineStage(logger, "fitbit_calories"):
        extract_specific_files_flat(
            zip_file_path=zip_path,
            prefix="Takeout/Fitbit/Global Export Data/calories",
            output_path=data_folder,
        )
        df = extract_json_file_data(
            folder_path=data_folder,
            file_name_prefix="calories",
            keys_to_keep=["dateTime", "value"],
        )
        log_system_resources(logger)
        with redirect_output_to_logger(logger, stdout_level=logging.DEBUG):
            logger.debug("Size of fitbit calories df_raw:")
            df.info()
            
        df = transform_time_series_data(df)
        with redirect_output_to_logger(logger, stdout_level=logging.DEBUG):
            logger.debug(f"Size of fitbit calories df_transformed:")
            df.info()
            
        if load_function:
            load_function(df, "fitbit_calories", TimeSeriesData)

        
    if cleanup:
        logger.info(f"Removing folder {data_folder} from zip...")
        shutil.rmtree(data_folder)

    return df
