from enum import StrEnum


class Source(StrEnum):
    FITBIT           = "fitbit"
    GITHUB           = "github"
    GYMGROUP         = "gymgroup"
    KINDLE           = "kindle"
    MACOS_COMMANDS   = "macos_commands"
    MACOS_SCREENTIME = "macos_screentime"
    STRONG           = "strong"


class Table(StrEnum):
    FITBIT_CALORIES      = "fitbit_calories"
    FITBIT_EXERCISE      = "fitbit_exercise"
    FITBIT_SLEEP         = "fitbit_sleep"
    FITBIT_STEPS         = "fitbit_steps"
    GITHUB_CONTRIBUTIONS = "github_contributions"
    GYMGROUP_VISITS      = "gymgroup_visits"
    KINDLE_READING       = "kindle_reading"
    MACOS_COMMANDS       = "macos_commands"
    MACOS_SCREENTIME     = "macos_screentime"
    STRONG_WORKOUTS      = "strong_workouts"

def inbox(name: str) -> str:
    return f"inbox/{name}"


def archive(name: str) -> str:
    return f"archive/{name}"


def table(name: str) -> str:
    return f"tables/{name}.parquet"
