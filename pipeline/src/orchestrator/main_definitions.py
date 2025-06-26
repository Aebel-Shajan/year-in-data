import dagster as dg
from orchestrator.resources.custom_io_manager import CustomIOManager
from orchestrator.definitions import fitbit_defs


resources = {
    "io_manager": CustomIOManager()
}

defs = dg.Definitions.merge(
    dg.Definitions(resources=resources),
    fitbit_defs.defs,
)


if __name__ == "__main__":
    import pathlib
    import os
    repo_root = pathlib.Path(__file__).parent.parent.parent.resolve()
    # Define DAGSTER_HOME relative to repo root, e.g. "<repo_root>/.dagster_home"
    dagster_home = repo_root / ".dagster"
    # Make sure the directory exists
    dagster_home.mkdir(parents=True, exist_ok=True)
    # Set the environment variable for this Python process
    os.environ["DAGSTER_HOME"] = str(dagster_home)
    dg.materialize(assets=[defs.resolve_assets_def("google_drive_files")], instance=dg.DagsterInstance.get())
    # fitbit_calories_job = defs.resolve_job_def("fitbit_calories_job")
    # fitbit_calories_job.execute_in_process(instance=dg.DagsterInstance.get())