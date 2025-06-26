import dagster as dg
from orchestrator.assets import fitbit_assets

fitbit_calories_job = dg.define_asset_job(
    name="fitbit_calories_job",
    selection=[
        fitbit_assets.fitbit_zip,
        fitbit_assets.fitbit_calories_jsons,
        fitbit_assets.raw_fitbit_calories,
        fitbit_assets.fitbit_calories,
    ],
)
