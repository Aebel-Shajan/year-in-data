"""
Pipeline stage orchestration.

Stages run in order: bronze → silver → gold

  bronze — jobs fetch raw data → inbox, then bronze models archive inbox → bronze store
  silver — parse archived bronze → silver Parquet
  gold   — aggregate silver → gold Parquet + web JSON

Each stage function accepts an optional `tags` set to run only assets with matching tags.
Tags: "fitbit", "github", "gymgroup", "kindle", "strong", "macos_commands", "macos_screentime"
"""

from __future__ import annotations

import traceback
from collections.abc import Collection
from datetime import date

from pipeline.asset import Model
from pipeline.models.bronze.fitbit_zip import fitbit_zip
from pipeline.models.bronze.github_api_response import github_api_response
from pipeline.models.bronze.gymgroup_api import gymgroup_api
from pipeline.models.bronze.kindle_zip import kindle_zip
from pipeline.models.bronze.macos_commands import macos_commands as bronze_macos_commands
from pipeline.models.bronze.macos_screentime import macos_screentime as bronze_macos_screentime
from pipeline.models.bronze.strong_csv import strong_csv
from pipeline.models.silver.fitbit_calories import fitbit_calories
from pipeline.models.silver.fitbit_exercise import fitbit_exercise
from pipeline.models.silver.fitbit_sleep import fitbit_sleep
from pipeline.models.silver.fitbit_steps import fitbit_steps
from pipeline.models.silver.github_contributions import github_contributions
from pipeline.models.silver.gymgroup_visits import gymgroup_visits
from pipeline.models.silver.kindle_reading import kindle_reading
from pipeline.models.silver.macos_commands import macos_commands
from pipeline.models.silver.macos_screentime import macos_screentime
from pipeline.models.silver.strong_workouts import strong_workouts
from pipeline.models.gold.daily_calories import daily_calories
from pipeline.models.gold.daily_commands import daily_commands
from pipeline.models.gold.daily_contributions import daily_contributions
from pipeline.models.gold.daily_exercise import daily_exercise
from pipeline.models.gold.daily_gym_visits import daily_gym_visits
from pipeline.models.gold.daily_reading import daily_reading
from pipeline.models.gold.daily_screen_time import daily_screen_time
from pipeline.models.gold.daily_sleep import daily_sleep
from pipeline.models.gold.daily_steps import daily_steps
from pipeline.models.gold.daily_workouts import daily_workouts
from pipeline.config import Config, Secrets
from pipeline.r2 import R2Client

BRONZE_MODELS = [
    Model(fitbit_zip,              "fitbit",          "bronze/inbox/fitbit",           "bronze/fitbit"),
    Model(github_api_response,     "github",          "bronze/inbox/github",           "bronze/github"),
    Model(gymgroup_api,            "gymgroup",        "bronze/inbox/gymgroup",         "bronze/gymgroup"),
    Model(kindle_zip,              "kindle",          "bronze/inbox/kindle",           "bronze/kindle"),
    Model(bronze_macos_commands,   "macos_commands",  "bronze/inbox/macos_commands",   "bronze/macos_commands"),
    Model(bronze_macos_screentime, "macos_screentime","bronze/inbox/macos_screentime", "bronze/macos_screentime"),
    Model(strong_csv,              "strong",          "bronze/inbox/strong",           "bronze/strong"),
]

SILVER_MODELS = [
    Model(fitbit_calories,      "fitbit",          "bronze/fitbit",          "silver/fitbit/calories.parquet"),
    Model(fitbit_exercise,      "fitbit",          "bronze/fitbit",          "silver/fitbit/exercise.parquet"),
    Model(fitbit_sleep,         "fitbit",          "bronze/fitbit",          "silver/fitbit/sleep.parquet"),
    Model(fitbit_steps,         "fitbit",          "bronze/fitbit",          "silver/fitbit/steps.parquet"),
    Model(github_contributions, "github",          "bronze/github",          "silver/github/contributions.parquet"),
    Model(gymgroup_visits,      "gymgroup",        "bronze/gymgroup",        "silver/gymgroup/visits.parquet"),
    Model(kindle_reading,       "kindle",          "bronze/kindle",          "silver/kindle/reading.parquet"),
    Model(macos_commands,       "macos_commands",  "bronze/macos_commands",  "silver/macos_commands/commands.parquet"),
    Model(macos_screentime,     "macos_screentime","bronze/macos_screentime","silver/macos_screentime/app_usage.parquet"),
    Model(strong_workouts,      "strong",          "bronze/strong",          "silver/strong/workouts.parquet"),
]

GOLD_MODELS = [
    Model(daily_calories,     "fitbit",          "silver/fitbit/calories.parquet",              "gold/fitbit/daily_calories.parquet",                "kcal",    "Calories burned"),
    Model(daily_exercise,     "fitbit",          "silver/fitbit/exercise.parquet",              "gold/fitbit/daily_exercise.parquet",                "minutes", "Active minutes"),
    Model(daily_sleep,        "fitbit",          "silver/fitbit/sleep.parquet",                 "gold/fitbit/daily_sleep.parquet",                   "hours",   "Sleep duration"),
    Model(daily_steps,        "fitbit",          "silver/fitbit/steps.parquet",                 "gold/fitbit/daily_steps.parquet",                   "steps",   "Steps"),
    Model(daily_gym_visits,   "gymgroup",        "silver/gymgroup/visits.parquet",              "gold/gymgroup/daily_gym_visits.parquet",             "minutes", "Gym duration"),
    Model(daily_workouts,     "strong",          "silver/strong/workouts.parquet",              "gold/strong/daily_workouts.parquet",                "minutes", "Workout duration"),
    Model(daily_reading,      "kindle",          "silver/kindle/reading.parquet",               "gold/kindle/daily_reading.parquet",                 "minutes", "Reading time"),
    Model(daily_commands,     "macos_commands",  "silver/macos_commands/commands.parquet",      "gold/macos_commands/daily_commands.parquet",        "count",   "Shell commands"),
    Model(daily_contributions,"github",          "silver/github/contributions.parquet",         "gold/github/daily_contributions.parquet",           "commits", "GitHub contributions"),
    Model(daily_screen_time,  "macos_screentime","silver/macos_screentime/app_usage.parquet",   "gold/macos_screentime/daily_screen_time.parquet",   "minutes", "Screen time"),
]


def run_bronze(r2: R2Client, secrets: Secrets, config: Config, tags: Collection[str] | None = None) -> list[str]:
    """Run bronze models, filtered by config tags (or explicit tags override)."""
    failures: list[str] = []
    for model in _filter(BRONZE_MODELS, config, tags):
        print(f"── {model.output_key} ──────────────────────")
        try:
            model.fn(r2, model.input_key, model.output_key, secrets=secrets, config=config)
        except Exception:
            traceback.print_exc()
            failures.append(model.output_key)
    return failures


def run_silver(
    r2: R2Client,
    config: Config,
    start: date | None = None,
    end: date | None = None,
    tags: Collection[str] | None = None,
) -> list[str]:
    """Run silver models, filtered by config tags (or explicit tags override)."""
    failures: list[str] = []
    for model in _filter(SILVER_MODELS, config, tags):
        name = model.output_key.rsplit("/", 1)[-1].removesuffix(".parquet")
        print(f"── {name} ──────────────────────")
        try:
            model.fn(r2, model.input_key, model.output_key, start=start, end=end)
        except Exception:
            traceback.print_exc()
            failures.append(name)
    return failures


def run_gold(
    r2: R2Client,
    config: Config,
    start: date | None = None,
    end: date | None = None,
    dry_run: bool = False,
    tags: Collection[str] | None = None,
) -> list[str]:
    """Run gold models, filtered by config tags (or explicit tags override)."""
    failures: list[str] = []
    for model in _filter(GOLD_MODELS, config, tags):
        name = model.output_key.rsplit("/", 1)[-1].removesuffix(".parquet")
        print(f"── {name} ──────────────────────")
        try:
            model.fn(r2, model.input_key, model.output_key, model.unit, model.label, start=start, end=end, dry_run=dry_run)
        except Exception:
            traceback.print_exc()
            failures.append(name)
    return failures


# ── Internal helpers ──────────────────────────────────────────────────────────

def _filter(models: list[Model], config: Config, tags: Collection[str] | None = None) -> list[Model]:
    """Filter models by tag. Explicit tags override config; config tags_to_run/tags_to_ignore apply otherwise."""
    if tags is not None:
        return [m for m in models if m.tag in tags]
    if config.tags_to_run:
        models = [m for m in models if m.tag in config.tags_to_run]
    if config.tags_to_ignore:
        models = [m for m in models if m.tag not in config.tags_to_ignore]
    return models
