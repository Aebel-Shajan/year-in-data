import dagster as dg
from orchestrator.assets import common_assets, github_assets


asset_selection = (
    dg.AssetSelection.assets(common_assets.landing_zone).downstream() |
    dg.AssetSelection.assets(github_assets.github_repo_contribution_jsons).downstream()
)

run_pipeline_job = dg.define_asset_job(
    name="run_pipeline_job",
    selection=asset_selection,
)

download_drive_files_job = dg.define_asset_job(
    name="download_drive_files_job",
    selection=dg.AssetSelection.assets(common_assets.google_drive_files)
)

