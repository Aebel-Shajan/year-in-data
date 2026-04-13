"""
Entry point for the yearly data pipeline.

  uv run python -m pipeline.main
"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path
from types import ModuleType

from pipeline.config import PipelineConfig
from pipeline.jobs import (
    aggregate,
    export,
    fitbit,
    github,
    gymgroup,
    kindle,
    macos_commands,
    macos_screentime
)
from pipeline.r2 import make_client


# list order determines order to run job 
ALL_JOBS = [
    fitbit,
    github,
    gymgroup,
    kindle,
    macos_commands,
    macos_screentime, 
    aggregate,
    export,
]


def run_pipeline(config: PipelineConfig) -> None:
    r2 = make_client(config)
    jobs_to_run = []
    for job in ALL_JOBS:
        job_name = get_module_name(job)
        run_job = not config.jobs_to_run or job_name in config.jobs_to_run
        if run_job:
            jobs_to_run.append(job)


    failures: list[str] = []

    for index, job in enumerate(jobs_to_run):
        try:
            job_name = get_module_name(job)
            print(f"{index}. running {job_name}...")
            job.run_job(r2, config)
        except Exception:
            traceback.print_exc()
            failures.append(job_name)

    if failures:
        print(f"\n✗ Failed: {', '.join(failures)}")
        sys.exit(1)
    print("\nDone.")


def get_module_name(module: ModuleType) -> str:
    return module.__name__.split('.')[-1]


if __name__ == "__main__":
    config = PipelineConfig.load()
    run_pipeline(config)
