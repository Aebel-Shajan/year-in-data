import json
import logging
import os
import shutil
from pathlib import Path
from typing import Callable, Optional

import pandas as pd
import pandera as pa
from pandera.typing.pandas import DataFrame

from yd_extractor.utils.pipeline_stage import PipelineStage
from yd_extractor.kindle.schemas import AsinMap, RawAsinMap
from yd_extractor.utils.utils import extract_specific_files_flat

logger = logging.getLogger(__name__)


def extract_book_data_from_jsons(file_names, output_path):
    full_data = []
    for file_name in file_names:
        with open(output_path / file_name, "r", encoding="utf-8") as file:
            content = file.read()
            if '"origin":{"originType":"Purchase"}' in content:
                try:
                    file.seek(0)
                    json_data = json.load(file)
                    full_data.append(
                        {
                            "purchase_date": json_data["rights"][0]["acquiredDate"],
                            "asin": json_data["resource"]["ASIN"],
                            "product_name": json_data["resource"]["Product Name"],
                        }
                    )
                except:
                    logger.warning(f"Error whilst loading data from {file_name}")

    logger.info(f"Extracted data from {len(full_data)} files.")
    return full_data


@pa.check_types
def extract_asin_map(
    output_path: Path,
    zip_file_path: Path,
) -> DataFrame[RawAsinMap]:
    search_prefix = "Digital.Content.Ownership/Digital.Content.Ownership."
    extract_specific_files_flat(
        zip_file_path,
        search_prefix,
        output_path,
    )
    file_prefix = "Digital.Content.Ownership."
    file_names = [f for f in os.listdir(output_path) if f.startswith(file_prefix)]
    if len(file_names) == 0:
        logger.error(f"No files found with prefix: {file_prefix}")

    full_data = extract_book_data_from_jsons(file_names, output_path)
    df = pd.DataFrame(full_data)
    RawAsinMap.validate(df)
    return df


@pa.check_types
def transform_asin_map(df: DataFrame[RawAsinMap]) -> DataFrame[AsinMap]:
    df = df.drop("purchase_date", axis=1)
    df = df.groupby("asin").aggregate({"product_name": "first"}).reset_index()
    df["product_name"] = df["product_name"].apply(lambda name: name.split(":")[0])

    AsinMap.validate(df)
    return df


def process_asin_map(
    inputs_folder: Path,
    zip_path: Path,
    cleanup: bool = True,
    load_function: Optional[Callable[[pd.DataFrame, str], None]] = None,
    
) -> DataFrame[AsinMap]:
    df = AsinMap.empty()
    with PipelineStage(logger, "kindle_asin_map"):
        data_folder = inputs_folder / "kindle_asin_map"
        df = extract_asin_map(data_folder, zip_path)
        df = transform_asin_map(df)
        if load_function:
            load_function(df, "kindle_asin_map")

    if cleanup:
        logger.info(f"Removing folder {data_folder} from zip...")
        shutil.rmtree(data_folder)
    return df


if __name__ == "__main__":
    df = process_asin_map(
        Path("data/input"),
        Path("data/input/Kindle.zip"),
    )
