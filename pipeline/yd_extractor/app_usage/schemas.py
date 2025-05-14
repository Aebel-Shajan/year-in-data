import pandera as pa
from pandera.typing.pandas import Series
from typing import Optional

class RawAppUsageScreenTime(pa.DataFrameModel):
    class Config:
        coerce=True
    
    app_name: Series[str] = pa.Field(
        alias="App name",
        nullable=True,
    )
    date: Series[str] =  pa.Field(
        alias="Date",
        nullable=True,
    )
    time: Series[object] = pa.Field(
        alias='Time',
        nullable=True,
    )
    duration: Series[object] = pa.Field(
        alias="Duration",
        nullable=True,
    )
    
    
class AppUsageScreenTime(pa.DataFrameModel):
    app_name: Series[str] = pa.Field()
    date: Series[pa.Timestamp] = pa.Field()
    time: Series[object]  = pa.Field()
    duration_minutes: Series[int] = pa.Field()
    image: Optional[Series[str]] = pa.Field()
    