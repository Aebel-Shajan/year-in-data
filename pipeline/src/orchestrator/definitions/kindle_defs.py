from orchestrator.assets import kindle_assets
import dagster as dg


all_assets = dg.load_assets_from_modules(
    [
        kindle_assets,
    ]
)

defs = dg.Definitions(
    assets=all_assets,
)