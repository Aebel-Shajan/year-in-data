import json
import logging
import os
from pathlib import Path

import pandas as pd
import pandera as pa
from pandera.typing.pandas import DataFrame

from transformations.kindle.schemas import AsinMap, RawAsinMap
from transformations.utils.io import extract_specific_files_flat

logger = logging.getLogger(__name__)


def extract_digital_content_jsons(zip_path: str, output_path: str) -> str:
    search_prefix = "Digital.Content.Ownership/Digital.Content.Ownership."
    extract_specific_files_flat(
        zip_path,
        search_prefix,
        output_path,
    )
    return output_path


@pa.check_types
def extract_asin_map(json_folder: str) -> DataFrame[RawAsinMap]:
    file_prefix = "Digital.Content.Ownership."
    file_names = [f for f in os.listdir(json_folder) if f.startswith(file_prefix)]
    if len(file_names) == 0:
        logger.error(f"No files found with prefix: {file_prefix}")

    full_data = []
    for file_name in file_names:
        with open(json_folder + "/" + file_name, "r", encoding="utf-8") as file:
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

