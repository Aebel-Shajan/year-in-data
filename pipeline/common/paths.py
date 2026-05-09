from enum import StrEnum


class Source(StrEnum):
    FITBIT           = "fitbit"
    GITHUB           = "github"
    GYMGROUP         = "gymgroup"
    KINDLE           = "kindle"
    MACOS_COMMANDS   = "macos_commands"
    MACOS_SCREENTIME = "macos_screentime"
    GARMIN           = "garmin"
    STRONG           = "strong"


class Table(StrEnum):
    FITBIT_CALORIES      = "fitbit_calories"
    FITBIT_EXERCISE      = "fitbit_exercise"
    FITBIT_SLEEP         = "fitbit_sleep"
    FITBIT_STEPS         = "fitbit_steps"
    GARMIN_ACTIVITIES    = "garmin_activities"
    GARMIN_WELLNESS      = "garmin_wellness"
    GITHUB_CONTRIBUTIONS = "github_contributions"
    GYMGROUP_VISITS      = "gymgroup_visits"
    KINDLE_READING       = "kindle_reading"
    MACOS_COMMANDS       = "macos_commands"
    MACOS_SCREENTIME     = "macos_screentime"
    STRONG_WORKOUTS      = "strong_workouts"

    DAILY_FITBIT_CALORIES      = "daily_fitbit_calories"
    DAILY_FITBIT_EXERCISE      = "daily_fitbit_exercise"
    DAILY_FITBIT_SLEEP         = "daily_fitbit_sleep"
    DAILY_FITBIT_STEPS         = "daily_fitbit_steps"
    DAILY_GITHUB_CONTRIBUTIONS = "daily_github_contributions"
    DAILY_GYMGROUP_VISITS      = "daily_gymgroup_visits"
    DAILY_KINDLE_READING       = "daily_kindle_reading"
    DAILY_MACOS_COMMANDS       = "daily_macos_commands"
    DAILY_MACOS_SCREENTIME     = "daily_macos_screentime"
    DAILY_STRONG_WORKOUTS      = "daily_strong_workouts"

def construct_inbox_path(name: str) -> str:
    return f"inbox/{name}"


def construct_archive_path(name: str) -> str:
    return f"archive/{name}"


def construct_table_path(name: str) -> str:
    return f"tables/{name}.parquet"
