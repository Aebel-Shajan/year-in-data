import json
import logging
import os
import sqlite3
from typing import Callable, Optional
import zipfile
from pathlib import Path

import gdown
import pandas as pd
import pandera as pa

from yd_extractor.utils.logger import redirect_output_to_logger
from yd_extractor.utils.pandas import get_range_for_df_column

# Setup logger
logger = logging.getLogger(__name__)


def load_graphql_query(file_path: str) -> str:
    """
    Load a GraphQL query from a file.

    Parameters
    ----------
    file_path : str
        The path to the file containing the GraphQL query.

    Returns
    -------
    str
        The GraphQL query as a string.
    """
    with open(file_path, "r") as file:
        query = file.read()
    return query


def write_db_to_jsons(db_path: str, output_path: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table_name in tables:
        table_name = table_name[0]
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]

        # Convert to list of dictionaries
        data = [dict(zip(columns, row)) for row in rows]

        # Write to JSON file
        with open(f"{output_path}/{table_name}.json", "w") as json_file:
            json.dump(data, json_file, indent=4)

    conn.close()


def get_latest_file(folder_path: Path, file_name_glob: str) -> Path:
    """Gets the latest file matching the glob pattern in the specified folder.

    Args:
        folder_path (Path): Path where desired file is.
        file_name_glob (str): Name/pattern the file matches.

    Raises:
        FileNotFoundError: Raise if folder_path does not exist.
        FileNotFoundError: Raised if no files found in provided folder path.

    Returns:
        Path: The path to the latest file.
    """
    if not os.path.exists(folder_path):
        error_message = f"Provided folder path {folder_path} does not exist."
        logger.error(error_message)
        raise FileNotFoundError(error_message)

    files = list(folder_path.glob(file_name_glob))
    if len(files) == 0:
        error_message = (
            f"No files found in {folder_path}, that matches glob {file_name_glob}"
        )
        logger.error(error_message)
        raise FileNotFoundError(error_message)

    # Search for most recent file
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]


def extract_specific_files_flat(zip_file_path: Path, prefix: str, output_path: Path):
    """
    Extracts specific files which have the same prefix from a ZIP archive and saves
    them to the given output directory without preserving their original folder
    structure.

    Args:
        zip_file_path (Path): Path to zip file.
        prefix (str): Prefix of files we want to extract.
        output_path (Path): Output directory to save the files to.
    """
    # Ensure the output directory exists
    os.makedirs(output_path, exist_ok=True)

    logger.info(
        f"Extracting files from '{os.path.relpath(zip_file_path)}'"
        f"\nwhich have prefix '{prefix}' "
        f"\ninto '{os.path.relpath(output_path)}' ..."
    )

    # Open the ZIP file
    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:

        for file_name in zip_ref.namelist():
            if file_name.startswith(prefix):
                # Extract the file to a temp location
                with zip_ref.open(file_name) as source_file:
                    # Get only the filename, ignoring directories
                    file_name = os.path.basename(file_name)
                    out_file_path = os.path.join(output_path, file_name)

                    # Write the extracted file to the output directory
                    with open(out_file_path, "wb") as output_file:
                        output_file.write(source_file.read())


def download_files_from_drive(
    input_data_folder: Path,
    env_vars: dict,
):
    if env_vars["DRIVE_SHARE_URL"] is None:
        raise Exception("Expected DRIVE_SHARE_URL in .env folder!")
    logger.info("🟡 Downloading data from google drive...")

    gdown.download_folder(
        url=env_vars["DRIVE_SHARE_URL"],
        output=str(input_data_folder.absolute()),
        use_cookies=False,
        quiet=True,
    )
    logger.info("✅ Finished downloading data from google drive!")
    


def get_metadata_from_schema(
    schema: pa.DataFrameModel,
    df: Optional[pd.DataFrame]=None,
) -> dict:
    metadata = schema.get_metadata()
    schema_name = list(metadata.keys())[0]
    column_metadata_dict = metadata[schema_name]["columns"]
    for column in column_metadata_dict.keys():
        if not column_metadata_dict[column]:
            column_metadata_dict[column] = {}
        if "tag" in column_metadata_dict[column].keys():
            if column_metadata_dict[column]["tag"] == "value_column": 
                logger.info(f"Getting range for {column} in {schema_name}")
                range = [0, 1]
                if df is not None:
                    range = get_range_for_df_column(df, column)
                column_metadata_dict[column]["range"] = range
    return metadata

        
def create_load_function(output_data_folder: str) -> Callable:
    def load_function(df: pd.DataFrame, name: str, schema: pa.DataFrameModel):
        save_path = output_data_folder / (name + ".csv")
        logger.info(f"Saving file into {save_path}..")
        df.to_csv(save_path, index=False)

        # Save to a JSON file
        metadata = get_metadata_from_schema(schema, df)
        output_file = output_data_folder / "metadata" / (name + "_metadata.json")
        with open(output_file, "w") as file:
            json.dump(metadata, file, indent=2)
            
    return load_function


