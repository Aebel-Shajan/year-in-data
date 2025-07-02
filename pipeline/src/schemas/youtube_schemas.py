import pandera as pa
from pandera.typing.pandas import Series, DateTime



class RawYoutubeWatchHistory(pa.DataFrameModel):
    datetime_str: Series[str] = pa.Field()
    video_name: Series[str] = pa.Field()
    video_url: Series[str] = pa.Field()
    channel_name: Series[str] = pa.Field()
    channel_url: Series[str] = pa.Field()
    

class YoutubeWatchHistory(pa.DataFrameModel):
    video_name: Series[str] = pa.Field(
        metadata={
            "tag": "category_column"
        }
    )
    video_url: Series[str] = pa.Field(
        metadata={
            "tag": "link_column"
        }
    )
    channel_name: Series[str] = pa.Field(
        metadata={
            "tag": "category_column"
        }
    )
    channel_url: Series[str] = pa.Field(
        metadata={
            "tag": "link_column"
        }
    )
    datetime: Series[DateTime] = pa.Field(
        metadata={
            "tag": "date_column"
        }
    )
    video_type: Series[str] = pa.Field(
        metadata={
            "tag": "category_column"
        }
    )