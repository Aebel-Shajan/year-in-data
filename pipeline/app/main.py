from enum import Enum
import os
import pathlib
import shutil
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from yd_extractor.fitbit.schemas import FitbitSleep
from yd_extractor.utils.io import get_metadata_from_schema
from yd_extractor import fitbit
import logging
import pandas as pd
import pandera as pa
from sqlalchemy import create_engine, inspect
engine = create_engine('sqlite:///year_in_data.db')
logger= logging.getLogger()

app = FastAPI()
inputs_folder = pathlib.Path("temp_uploads")
inputs_folder.mkdir(parents=True, exist_ok=True)

origins = [
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello world"}


def pascal_to_snake(pascal_str):
    """
    Convert a PascalCase string to snake_case.
    
    Args:
        pascal_str (str): The PascalCase string to convert
        
    Returns:
        str: The converted snake_case string
    
    Examples:
        >>> pascal_to_snake("HelloWorld")
        "hello_world"
        >>> pascal_to_snake("HTTPResponse")
        "http_response"
    """
    if not pascal_str:
        return ""
    
    # Start with the first character in lowercase
    result = pascal_str[0].lower()
    
    # Process the rest of the string
    for char in pascal_str[1:]:
        if char.isupper():
            # Add underscore before uppercase letters
            result += "_" + char.lower()
        else:
            result += char
            
    return result

schemas = [
    FitbitSleep,
]

SCHEMA_MAP = {pascal_to_snake(schema.__name__): schema for schema in schemas}
SCHEMA_NAME_MAP = {pascal_to_snake(m.__name__): pascal_to_snake(m.__name__) for m in schemas}
SchemaNameMap = Enum("RouteName", SCHEMA_NAME_MAP)

@app.get("/data/metadata/{name}")
async def get_data_for_source(name: SchemaNameMap):
    name = name.value
    if name not in SCHEMA_MAP.keys():
        raise HTTPException(404, f"Route not found. Must be one of {SCHEMA_MAP.keys()}")
    
    try:
        validate_table(name)
        with engine.connect() as conn:
            df = pd.read_sql(f"SELECT * FROM {name}", conn)
            metadata = get_metadata_from_schema(SCHEMA_MAP[name], df)
            return metadata
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the file: {str(e)}"
        )

# Helper: validate table name
def validate_table(table_name: str):
    inspector = inspect(engine)
    if table_name not in inspector.get_table_names():
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' does not exist.")

# GET all rows from a table
@app.get("/data/{table_name}")
def get_table_data(table_name: str):
    validate_table(table_name)
    with engine.connect() as conn:
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    return df.to_dict(orient="records")


def load_function(df: pd.DataFrame, name: str, schema_model: pa.DataFrameModel):
    df.to_sql(name=name, con=engine, if_exists="replace")
    

@app.post("/google")
async def upload_google_zip_file(file: UploadFile):
    logger.info("Uploading zip file...")
    # Validate that uploaded file is a zip
    if not file.filename.endswith(".zip"):
        raise HTTPException(
            status_code=406,
            detail="Uploaded file must be a zip!"
        )
    
    # Save file temporarily to file system
    inputs_folder = pathlib.Path("temp_uploads")
    zip_file_path = inputs_folder / file.filename
    with zip_file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        del file
        logger.info("file copied into file system...")
        
    # initalise uploaded_sources
    uploaded_sources = []
        
    try:
        logger.info("Reading data into db...")
        fitbit.process_sleep(
            inputs_folder=inputs_folder,
            zip_path=zip_file_path,
            load_function=load_function,
            cleanup=False
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the file: {str(e)}"
        )
    finally:
        os.remove(zip_file_path)
        
    return {
        "status": "success",
        "message": "Successfully uploaded and processed amazon data.",
        "data": uploaded_sources
    }