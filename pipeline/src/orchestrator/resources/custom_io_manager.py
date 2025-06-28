from dataclasses import dataclass, asdict
import os
from pathlib import Path
import yaml
import sqlite3
import pandas as pd
from dagster import ConfigurableIOManager
import dagster as dg
from typing import Literal


@dataclass
class CatalogItem:
    asset_key: str
    type: str
    location: str
    kinds: str


# Why use a CustomIOManager?

class CustomIOManager(ConfigurableIOManager):
    """CustomIOManager which handle loading input/output file/folder paths and pandas 
    dataframes.
    
    Note:
        Q) Why use a CustomIOManager? 
        A) I wanted a way to handle loading files and sqlite tables without having it
        entirely in memory or have it pickled. 
        
        Q) Why not use DuckDBPandasIOManager?
        A) I tried but couldn't get it to work with files/file paths. Also I'm more used 
        to sqlite3. Although I want to start using duckdb because I heard it handles 
        schemas better and you can attach metadata to table columns.
    """
    catalog_db_path: str = "data/data_catalog.db"

    def _ensure_catalog_table(self):
        with sqlite3.connect(self.catalog_db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS catalog (
                    asset_key TEXT PRIMARY KEY,
                    type TEXT,
                    location TEXT,
                    kinds TEXT
                )
                """
            )

    def _update_catalog(self, catalog_item: CatalogItem):
        self._ensure_catalog_table()
        with sqlite3.connect(self.catalog_db_path) as conn:
            conn.execute(
                """
                INSERT INTO catalog (asset_key, type, location, kinds)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(asset_key) DO UPDATE SET
                    type=excluded.type,
                    location=excluded.location,
                    kinds=excluded.kinds
                """,
                (
                    catalog_item.asset_key,
                    catalog_item.type,
                    catalog_item.location,
                    ",".join(catalog_item.kinds) if isinstance(catalog_item.kinds, list) else catalog_item.kinds,
                ),
            )

    def _get_asset_info(self, asset_key: str) -> dict:
        self._ensure_catalog_table()
        with sqlite3.connect(self.catalog_db_path) as conn:
            cur = conn.execute(
                "SELECT asset_key, type, location, kinds FROM catalog WHERE asset_key = ?",
                (asset_key,),
            )
            row = cur.fetchone()
            if not row:
                raise KeyError(f"Key '{asset_key}' not found in {self.catalog_db_path}")
            return {
                "asset_key": row[0],
                "type": row[1],
                "location": row[2],
                "kinds": row[3].split(",") if row[3] else [],
            }

    def handle_output(self, context: dg.OutputContext, obj: pd.DataFrame | str):
        asset_key = context.asset_key.path[-1]  # assumes single-level asset key
        asset_kinds = context.asset_spec.kinds
        medallion = "other"
        medallion_list = {"bronze", "silver", "gold", "other"}
        for medallion in medallion_list:
            Path(f"data/{medallion}").mkdir(exist_ok=True)
        if asset_kinds.intersection(medallion_list):
            medallion = list(asset_kinds.intersection(medallion_list))[0]

        if isinstance(obj, str):
            asset_catalog = CatalogItem(
                asset_key=asset_key,
                type="path",
                location=obj,
                kinds=list(asset_kinds),
            )
            context.log.info(
                f"Updated {self.catalog_db_path} with path for {asset_key}: {obj}"
            )
            context.add_output_metadata(
                {
                    **asdict(asset_catalog),
                }
            )
            self._update_catalog(asset_catalog)
        elif isinstance(obj, pd.DataFrame):
            db_path = f"data/{medallion}/{medallion}.db"

            asset_catalog = CatalogItem(
                asset_key=asset_key,
                type="dataframe",
                location=db_path,
                kinds=list(asset_kinds),
            )

            with sqlite3.connect(db_path) as conn:
                obj.to_sql(asset_key, conn, if_exists="replace", index=False)

            self._update_catalog(asset_catalog)
            context.log.info(
                f"Saved DataFrame to SQLite table '{asset_key}' and updated YAML"
            )
            context.add_output_metadata(
                {
                    "row_count": dg.MetadataValue.int(obj.shape[0]),
                    "preview": dg.MetadataValue.md(
                        obj.head(5).to_markdown(index=False)
                    ),
                    **asdict(asset_catalog),
                }
            )
        else:
            raise ValueError("Expected to handle strings (paths) or pandas DataFrames.")

    def load_input(self, context: dg.InputContext) -> str | pd.DataFrame:
        # assumes single-level asset key
        asset_key = context.upstream_output.asset_key.path[-1]  
        info = self._get_asset_info(asset_key)
        asset_kinds = set(info["kinds"])
        medallion = "other"
        if asset_kinds.intersection({"bronze", "silver", "gold"}):
            medallion = list(asset_kinds.intersection({"bronze", "silver", "gold"}))[0]


        if info["type"] == "path":
            context.log.info(
                f"Loading path for '{asset_key}' from YAML: {info['location']}"
            )
            return info["location"]

        elif info["type"] == "dataframe":
            db_path = f"data/{medallion}/{medallion}.db"
            with sqlite3.connect(db_path) as conn:
                df = pd.read_sql(f"SELECT * FROM {asset_key}", conn)
            context.log.info(f"Loaded DataFrame for '{asset_key}' from SQLite")
            return df

        else:
            raise ValueError(
                f"Unknown asset type '{info['type']}' for key '{asset_key}'"
            )
