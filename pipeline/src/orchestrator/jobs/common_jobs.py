import dagster as dg
from orchestrator.assets import common_assets, github_assets

run_pipeline_job = dg.define_asset_job(
    name="run_pipeline_job",
    selection=dg.AssetSelection.assets(common_assets.landing_zone).downstream(),
)