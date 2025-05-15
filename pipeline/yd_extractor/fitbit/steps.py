import logging
import shutil
from pathlib import Path
from typing import Callable, Optional

import pandas as pd

from yd_extractor.utils.pipeline_stage import PipelineStage
from yd_extractor.fitbit.utils import (extract_json_file_data,
                                       transform_time_series_data)
from yd_extractor.utils.utils import extract_specific_files_flat

logger = logging.getLogger(__name__)


def process_steps(
    inputs_folder: Path, 
    zip_path: Path, 
    cleanup: bool = True,
    load_function: Optional[Callable[[pd.DataFrame, str], None]] = None,
) -> pd.DataFrame:

    # Unzip and extract calories jsons from zip file.
    with PipelineStage(logger, "fitbit_steps"):
        data_folder = inputs_folder / "steps"
        extract_specific_files_flat(
            zip_file_path=zip_path,
            prefix="Takeout/Fitbit/Global Export Data/steps",
            output_path=data_folder,
        )
        df = extract_json_file_data(
            folder_path=data_folder,
            file_name_prefix="steps",
            keys_to_keep=["dateTime", "value"],
        )
        df = transform_time_series_data(df)
        if load_function:
            load_function(df, "fitbit_steps")


    if cleanup:
        shutil.rmtree(data_folder)

    return df
