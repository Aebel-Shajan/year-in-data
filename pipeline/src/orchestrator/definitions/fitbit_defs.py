from orchestrator.assets import fitbit_assets
from orchestrator.jobs import fitbit_jobs
import dagster as dg


all_assets = dg.load_assets_from_modules(
    [
        fitbit_assets,
    ]
)

defs = dg.Definitions(
    assets=all_assets,
    jobs=[
        fitbit_jobs.fitbit_calories_job,
    ],
)