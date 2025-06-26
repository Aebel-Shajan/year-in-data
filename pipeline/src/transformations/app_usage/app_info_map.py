import logging
from pathlib import Path
from typing import Callable, Optional

import pandas as pd
import pandera as pa
import requests
from bs4 import BeautifulSoup
from pandera.typing.pandas import DataFrame

from transformations.utils.pipeline_stage import PipelineStage
from transformations.app_usage.schemas import AppInfoMap, RawAppInfoMap
from transformations.utils.pandas import rename_df_from_schema

logger = logging.getLogger(__name__)


@pa.check_types
def extract_app_info_map(csv_file_path: str) -> DataFrame[RawAppInfoMap]:
    logger.info(f"Extracting app info data from {csv_file_path}...")
    with open(csv_file_path) as file:
        df = pd.read_csv(file)
    df = RawAppInfoMap.validate(df)
    return df


def get_play_store_icon(package_name: str) -> Optional[str]:
    url = f"https://play.google.com/store/apps/details"
    params = {"id": package_name, "hl": "en", "gl": "us"}
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.warning(f"Failed to fetch page for {package_name}: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    icon_tag = soup.find("img", {"alt": "Icon image"})
    if icon_tag and icon_tag.get("src", "").startswith(
        "https://play-lh.googleusercontent.com/"
    ):
        logger.info(f"Logo found for {package_name}")
        return icon_tag["src"]

    logger.warning(f"No logo found for {package_name}")
    return None


@pa.check_types
def transform_app_info_map(df: DataFrame[RawAppInfoMap]) -> DataFrame[AppInfoMap]:
    logger.info("Tranforming app info data...")
    df = rename_df_from_schema(df, RawAppInfoMap)
    df = df.dropna()
    df = df[~df["updated_time"].dt.year.isin([2009, 1970])]  # Removes system apps
    df = df[
        [
            "app_name",
            "package_name",
            "category",
        ]
    ]
    df
    df["image"] = df["package_name"].apply(get_play_store_icon)
    df["image"] = df["image"].fillna("")
    df = df.drop("package_name", axis=1)
    df = AppInfoMap.validate(df)
    return df


