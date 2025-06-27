import dagster as dg
from orchestrator.assets import fitbit_assets

fitbit_calories_job = dg.define_asset_job(
    name="fitbit_calories_job",
    selection=[
        dg.AssetSelection(fitbit_assets.fitbit_calories).downstream()
    ],
)
