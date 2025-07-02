import json
from typing import Optional
from app.models.table_schema import CategoryColumn, TableEventRecords, TableSchema, ValueColumn
from fastapi import APIRouter, Depends, HTTPException
from app.db.connection import get_connection
from orchestrator.main_definitions import defs
import pandas as pd
from pandera import DataFrameModel
from transformations.utils.io import to_snake_case
from transformations.utils.pandas import get_all_schema_models, get_range_for_df_column
from transformations.utils.dagster import get_all_gold_assets, get_dagster_type
import pandera.pandas as pa
from typing import List
import schemas
import dagster as dg

router = APIRouter(prefix="/tables")
# I wanted to define column sementic data in pandera schema column metadata.


def get_schema_metadata(assets_def: dg.AssetsDefinition) -> TableSchema:
    """Converts pandera schema metadata into a TableSchema object we defined."""
    schema_name = get_dagster_type(assets_def).display_name
    all_schemas: List[pa.DataFrameModel] = get_all_schema_models(schemas)
    schema_map = {
        schema.__name__: schema
        for schema in all_schemas
    }
    schema = schema_map[schema_name]
    pa_metadata = schema.get_metadata()
    schema_name = list(pa_metadata.keys())[0]
    column_metadata_dict: dict = pa_metadata[schema_name]["columns"]
    datetime_column: Optional[str] = None
    value_columns: dict[str, ValueColumn] = {}
    category_columns: dict[str, CategoryColumn] = {}
    
    df = pd.DataFrame()
    with get_connection() as conn:
        table_name = assets_def.key.to_user_string()
        print(table_name)
        try:
            # TODO: Instead of loading entire table, create new table to contain all ranges
            df = pd.read_sql(f"select * from {table_name} ;", con=conn)
        except:
            Exception(f"Error whilst trying to read table {table_name} to retrieve schema metadata")
    
    
    for column in column_metadata_dict.keys():
        column_metadata: dict = column_metadata_dict[column]
        if column_metadata is None:
            continue
        if "tag" in column_metadata.keys():
            column_tag = column_metadata_dict[column]["tag"]
            if column_tag == "datetime_column" or column_tag == "date_column":
                datetime_column = column
            elif column_tag == "value_column":
                range = (0, 10)
                if column in df.columns:
                    range = get_range_for_df_column(df, column)
                value_columns[column] = ValueColumn(
                    name=column,
                    units=column_metadata["units"],
                    range=range
                )
            elif column_tag == "category_column":
                image_column = None
                if "image_column" in column_metadata:
                    image_column = column_metadata["image_column"]
                category_columns[column] = CategoryColumn(
                    name=column,
                    image_column=image_column,
                )

    if datetime_column is None:
        raise ValueError(
            f"Expected schema {schema_name} to have datetime column! \n"
            "Schema metadata must include e.g. {'tag': 'datetime_column'} in its metadata."
        )
    if len(value_columns) == 0:
        raise ValueError(
            f"Expected schema  {schema_name} to have at least one value column! \n"
            "Schema must metadata include e.g. {'tag': 'value_column'} in its metadata."
        )
    return TableSchema(
        datetime_column=datetime_column,
        value_columns=value_columns,
        category_columns=category_columns
    )
    
@router.get("/list_all_tables")
def list_all_tables():
    gold_assets = get_all_gold_assets(defs)
    table_names = [asset.key.to_user_string() for asset in gold_assets]
    return table_names

@router.get("/{table_name}/{year}")
def get_table(
    table_name: str,
    year: int,
):
    gold_assets = get_all_gold_assets(defs)
    asset_map = {
        asset.key.to_user_string(): asset 
        for asset in gold_assets
    }
    
    type_names = [get_dagster_type(asset).display_name for asset in gold_assets]
    all_schemas: List[pa.DataFrameModel] = get_all_schema_models(schemas)
    schema_map = {
        schema.__name__: schema
        for schema in all_schemas
        if schema.__name__ in type_names
    }
    if not table_name in asset_map.keys():
        raise HTTPException(
            404, 
            f"Table not found. Must be one of {list(asset_map.keys())}",
        )
    asset = asset_map[table_name]
    schema_name = get_dagster_type(asset).display_name
    
    if not schema_name in schema_map.keys():
        raise HTTPException(
            404,
            f"No schema found for {table_name}. Available schemas: {list(schema_map.keys())}"
        )
    
    try:
        schema_metadata = get_schema_metadata(asset)
        date_col = schema_metadata.datetime_column
        with get_connection() as conn:
            df = pd.read_sql(f"select * from {table_name} where strftime('%Y', {date_col}) = '{year}'", con=conn)
            return TableEventRecords(
                schema=schema_metadata,
                records=df.to_dict(orient='records')
            )
    except Exception as e:
        raise HTTPException(
            500,
            detail=str(e)
        )