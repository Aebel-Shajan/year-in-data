from dataclasses import dataclass, asdict
import os
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


class CustomIOManager(ConfigurableIOManager):
    catalog_path: str = "data/data_catalog.yaml"

    def _update_catalog(self, catalog_item: CatalogItem):
        if os.path.exists(self.catalog_path):
            with open(self.catalog_path) as f:
                data = yaml.safe_load(f) or {}
        else:
            data = {}

        data[catalog_item.asset_key] = asdict(catalog_item)
        with open(self.catalog_path, "w") as f:
            yaml.safe_dump(data, f)

    def _get_asset_info(self, asset_key: str) -> CatalogItem:
        if not os.path.exists(self.catalog_path):
            raise FileNotFoundError(f"{self.catalog_path} not found")

        with open(self.catalog_path) as f:
            data = yaml.safe_load(f) or {}

        if asset_key not in data:
            raise KeyError(f"Key '{asset_key}' not found in {self.catalog_path}")

        return data[asset_key]

    def handle_output(self, context: dg.OutputContext, obj: pd.DataFrame | str):
        asset_key = context.asset_key.path[-1]  # assumes single-level asset key
        asset_kinds = context.asset_spec.kinds
        medallion = "other"
        if asset_kinds.intersection({"bronze", "silver", "gold"}):
            medallion = list(asset_kinds.intersection({"bronze", "silver", "gold"}))[0]

        if isinstance(obj, str):
            asset_catalog = CatalogItem(
                asset_key=asset_key,
                type="path",
                location=obj,
                kinds=list(asset_kinds),
            )
            context.log.info(
                f"Updated YAML {self.catalog_path} with path for {asset_key}: {obj}"
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
