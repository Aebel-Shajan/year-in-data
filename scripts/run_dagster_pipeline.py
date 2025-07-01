from orchestrator.main_definitions import defs
from transformations.utils.io import write_sqlite_db_to_csvs
from transformations.utils.pandas import get_all_schema_models
import transformations
import dagster as dg
from dotenv import load_dotenv
from pathlib import Path
import logging
import shutil

logger = logging.getLogger()

# For local dev
load_dotenv(Path(__file__).parent.parent / Path("pipeline/.env"))
instance = dg.DagsterInstance.get()

# defs.resolve_job_def("download_drive_files_job").execute_in_process(instance=instance)
# result = defs.resolve_job_def("run_pipeline_job").execute_in_process(instance=instance, raise_on_error=False)

write_sqlite_db_to_csvs(
    db_path="data/gold/gold.db",
    output_dir="data/output",
    schemas=get_all_schema_models(transformations)
)

shutil.copytree("data/output", "website/public/assets/data", dirs_exist_ok=True)
