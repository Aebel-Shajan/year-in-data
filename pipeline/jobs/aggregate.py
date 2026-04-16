"""
Aggregates job parquets into daily summary tables.
"""

from __future__ import annotations

from pipeline import r2 as R2
from pipeline.config import PipelineConfig
from pipeline.jobs import fitbit, github, gymgroup, kindle, macos_commands, macos_screentime, strong
from pipeline.paths import Table, table
from pipeline.r2 import R2Client

_AGGREGATIONS = [
    (Table.FITBIT_CALORIES,      fitbit.aggregate_calories),
    (Table.FITBIT_STEPS,         fitbit.aggregate_steps),
    (Table.FITBIT_EXERCISE,      fitbit.aggregate_exercise),
    (Table.FITBIT_SLEEP,         fitbit.aggregate_sleep),
    (Table.GITHUB_CONTRIBUTIONS, github.aggregate),
    (Table.GYMGROUP_VISITS,      gymgroup.aggregate),
    (Table.KINDLE_READING,       kindle.aggregate),
    (Table.MACOS_COMMANDS,       macos_commands.aggregate),
    (Table.MACOS_SCREENTIME,     macos_screentime.aggregate),
    (Table.STRONG_WORKOUTS,      strong.aggregate),
]


def aggregate_daily(r2: R2Client, config: PipelineConfig) -> None:
    for table_name, transform in _AGGREGATIONS:
        _agg(r2, table_name, transform)


def _agg(r2: R2Client, name: str, transform) -> None:
    input_key = table(name)
    output_key = table("daily_" + name)
    df = R2.load_parquet(r2, input_key)
    if df is None:
        print(f"[{input_key}] no data, skipping")
        return
    result = transform(df)
    R2.store_parquet(r2, output_key, result, sort_col="date", overwrite=True)
    print(f"[{output_key}] {len(result)} rows")
