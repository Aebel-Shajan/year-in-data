import pandas as pd

def parse_duration(duration: str) -> float:
    """Convert duration from the format `{hours}h {minutes}m` to milliseconds

    Parameters
    ----------
    duration : str
        Duration string in one of the formats:
            * `{hours}h {minutes}m`
            * `{hours}h`
            * `{minutes}m`

    Returns
    -------
    duration_ms : float
        Duration in milliseconds
    """

    def throw_error():
        raise ValueError("duration must have type like `{hours}h {minutes}m`")

    duration_ms = 0
    parts = duration.split()
    # Validation
    if len(parts) > 2 or len(parts) == 0:
        throw_error()
    for part in parts:
        if not part[:-1].isnumeric():
            throw_error()
        if not (part.endswith("h") or part.endswith("m")):
            throw_error()

    for index, part in enumerate(parts):
        if part.endswith("h") and index == 0:
            hours = part.rstrip("h")
            duration_ms += float(hours) * 60 * 1000
        elif part.endswith("m"):
            minutes = part.rstrip("m")
            duration_ms += float(minutes) * 1000

    return duration_ms


def check_columns_exist(df: pd.DataFrame, columns: list[str]) -> bool:
    """Checks if a given dataframe contains the provided columns.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe to check columns.
    columns : list[str]
        Columns to check.

    Returns
    -------
    bool
        True if dataframe contains all columns provided. False otherwise.
    """
    return set(columns).issubset(df.columns)
