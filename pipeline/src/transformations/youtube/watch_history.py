from bs4 import BeautifulSoup
from transformations.utils.io import extract_specific_files_flat
import logging
import pandas as pd
logger = logging.getLogger(__name__)

def extract_youtube_html(zip_path: str, output_folder: str) -> str:
    output_folder = "testdata/youtube"
    extract_specific_files_flat(
        zip_path,
        prefix="Takeout/YouTube and YouTube Music/history/watch-history.html",
        output_path=output_folder,
    )
    html_file_path = output_folder + "/watch-history.html"
    return html_file_path


def extract_youtube_watch_history_raw(html_path: str) -> pd.DataFrame:
    logger.info(
        "Finding all elements in watch history html file which contain watch history"
        " info."
    )
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml")
    
    content_cell_list = soup.find_all(
        name='div', 
        attrs={
            "class": 'content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1'
        }
    )
    logger.info(f"Found {len(content_cell_list)} elements to extract ihstory from.")
    errored_cells = []
    watch_history_list: list[dict] = []
    for index, content_cell in enumerate(content_cell_list):
        try:
            row = {}
            # Extract video link and name
            video_tag = content_cell.find('a', href=True)
            if video_tag is None:
                raise Exception("Video tag not found")
            row["video_name"] = video_tag.text.strip()
            row["video_url"] = video_tag['href'].strip()

            # Extract channel link and name (next <a> tag)
            channel_tag = video_tag.find_next('a', href=True)
            if channel_tag is None:
                raise Exception("Channel tag not found")
            row["channel_name"] = channel_tag.text.strip()
            row["channel_url"] = channel_tag['href'].strip()

            # Extract the date (text following the channel link)
            date_tag = channel_tag.next_sibling.next_sibling
            if date_tag is None:
                raise Exception("Date tag not found")
            row["datetime_str"] = date_tag.strip()
            watch_history_list.append(row)
        except Exception:
            errored_cells.append(content_cell)
    
    logger.info("finished extracting all watch history from html.")
    total_elements = len(content_cell_list)
    successful_elements = total_elements - len(errored_cells)
    logger.info(f"Extracted {successful_elements}/{total_elements}")
    return pd.DataFrame(watch_history_list)


def _parse_youtube_date_str(df: pd.DataFrame) -> pd.DataFrame:
    # fix in future convert to utc
    df["datetime_str"] = df["datetime_str"].str.replace("\u202F", " ").str.replace("\u00A0", " ")
    df["datetime_str"] = df["datetime_str"].str.removesuffix(" BST")
    df["datetime"] = pd.to_datetime(df["datetime_str"], format="%b %d, %Y, %I:%M:%S %p")
    df = df.sort_values(by=["datetime"]).reindex()
    df = df.drop(columns=["datetime_str"])
    return df


def _filter_videos(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df["video_url"].str.contains("watch")]
    return df


def _determine_video_type(df: pd.DataFrame) -> pd.DataFrame:
    # Filter only watchable content
    df["next_vid_datetime"] = df["datetime"].shift(-1)
    df["time_to_next_video"] = (
        (df["next_vid_datetime"] - df["datetime"])
    ).dt.total_seconds()
    # last element does not have next_vid_datetime
    df["time_to_next_video"] = df["time_to_next_video"].fillna(-1)
    # Filter vids not watched
    df = df[(df["time_to_next_video"] > 5) | (df["time_to_next_video"] == -1)]
    df.loc[df["time_to_next_video"] > 90, "video_type"] = "likely video"
    df.loc[df["time_to_next_video"] <= 90, "video_type"] = "likely short"
    df.loc[df["time_to_next_video"] == -1, "video_type"] = "unknown"
    df.loc[df["time_to_next_video"] > 3 * 60 * 60, "video_type"] = "unknown"
    df.loc[df["video_name"].str.contains("#"), "video_type"] = "likely short"
    # df.loc[df["time_to_next_video"]]
    return df


def transform_youtube_watch_history(df: pd.DataFrame) -> pd.DataFrame:
    df = _parse_youtube_date_str(df)
    df = _filter_videos(df)
    df = _determine_video_type(df)
    return df
