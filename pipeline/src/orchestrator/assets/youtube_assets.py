import dagster as dg
import pandas as pd
from orchestrator.assets.common_assets import landing_zone
from transformations.utils.io import get_latest_valid_zip
from transformations.youtube import watch_history
from schemas import youtube_schemas
from dagster_pandera import pandera_schema_to_dagster_type

@dg.asset(
    deps=[landing_zone],
    kinds={"bronze"}
)
def latest_youtube_zip(landing_zone: str) -> str:
    google_folder = landing_zone + "/google"
    zip_path = get_latest_valid_zip(
        google_folder,
        file_name_glob="*zip",
        expected_file_path="Takeout/YouTube and YouTube Music/history/watch-history.html",
    )
    if zip_path is None:
        raise dg.Failure("Couldn't find google takeout zip which contains youtube watch history html.")
    return zip_path



@dg.asset(
    deps=[latest_youtube_zip],
    kinds={"bronze"},
)
def youtube_watch_history_html(latest_youtube_zip: str) -> str:
    html_path = watch_history.extract_youtube_html(
        latest_youtube_zip,
        output_folder="data/bronze/stage/youtube"
    )
    return html_path


@dg.asset(
    deps=[youtube_watch_history_html],
    kinds={"silver"},
    dagster_type=pandera_schema_to_dagster_type(youtube_schemas.RawYoutubeWatchHistory)
)
def youtube_watch_history_raw(youtube_watch_history_html: str) -> pd.DataFrame:
    df = watch_history.extract_youtube_watch_history_raw(youtube_watch_history_html)
    return df

@dg.asset(
    deps=[youtube_watch_history_raw],
    kinds={"gold"},
    dagster_type=pandera_schema_to_dagster_type(youtube_schemas.YoutubeWatchHistory)
)
def youtube_watch_history(youtube_watch_history_raw: pd.DataFrame) -> pd.DataFrame:
    df = watch_history.transform_youtube_watch_history(youtube_watch_history_raw)
    return df