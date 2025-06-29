import pandera as pa
from pandera.typing.pandas import Series, DateTime


class YoutubeWatchHistory(pa.DataFrameModel):
    video_name: Series[str] = pa.Field(
        metadata={
            "tags": "category_column"
        }
    )
    video_url: Series[str] = pa.Field(
        metadata={
            "tags": "link_column"
        }
    )
    channel_name: Series[str] = pa.Field(
        metadata={
            "tags": "category_column"
        }
    )
    channel_url: Series[str] = pa.Field(
        metadata={
            "tags": "link_column"
        }
    )
    datetime: Series[DateTime] = pa.Field(
        metadata={
            "tags": "date_column"
        }
    )
    video_type: Series[str] = pa.Field(
        metadata={
            "tags": "category_column"
        }
    )