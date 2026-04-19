"""
Entry point for the yearly data pipeline.

  uv run python -m pipeline.main
"""

from __future__ import annotations

import sys
import traceback

from pipeline.common.config import PipelineConfig
from pipeline.jobs import JobFn
from pipeline.jobs.aggregate import aggregate_daily
from pipeline.jobs.export import export_to_web
from pipeline.jobs.fitbit import extract_fitbit
from pipeline.jobs.github import extract_github
from pipeline.jobs.gymgroup import extract_gymgroup
from pipeline.jobs.kindle import extract_kindle
from pipeline.jobs.macos_commands import extract_macos_commands
from pipeline.jobs.macos_screentime import extract_macos_screentime
from pipeline.common.r2 import make_client

# Order determines execution sequence
ALL_JOBS: list[JobFn] = [
    extract_fitbit,
    extract_github,
    extract_gymgroup,
    extract_kindle,
    extract_macos_commands,
    extract_macos_screentime,
    aggregate_daily,
    export_to_web,
]


def run_pipeline(config: PipelineConfig) -> None:
    r2 = make_client(config)

    jobs_to_run = [
        job for job in ALL_JOBS
        if not config.jobs_to_run or _job_name(job) in config.jobs_to_run
    ]

    failures: list[str] = []

    for index, job in enumerate(jobs_to_run):
        name = _job_name(job)
        try:
            print(f"{index}. running {name}...")
            job(r2, config)
        except Exception:
            traceback.print_exc()
            failures.append(name)

    if failures:
        print(f"\n✗ Failed: {', '.join(failures)}")
        sys.exit(1)
    print("\nDone.")


def _job_name(job: JobFn) -> str:
    # e.g. pipeline.jobs.fitbit → fitbit; aggregate_daily → aggregate
    module = getattr(job, "__module__", "")
    return module.split(".")[-1]


if __name__ == "__main__":
    config = PipelineConfig.load()
    run_pipeline(config)
