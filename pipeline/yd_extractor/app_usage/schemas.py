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
    category: Optional[Series[str]] = pa.Field()


class RawAppInfoMap(pa.DataFrameModel):
    class Config:
        coerce = True
        
    app_name: Series[str] = pa.Field(
        alias="App name",
        nullable=True,
    )
    package_name: Series[str] = pa.Field(
        alias="Package name",
        nullable=True
    )
    app_version: Series[str] = pa.Field(
        alias="App version",
        nullable=True,
    )
    app_version_code: Series[int] = pa.Field(
        alias="App version code",
        nullable=True,
        default=0,
    )
    updated_time: Series[pa.Timestamp] = pa.Field(
        alias="Updated time",
        nullable=True,
    )
    category: Series[str] = pa.Field(
        alias="Category",
        nullable=True,
    )
    installed: Series[str] = pa.Field(
        alias="Installed",
        nullable=True,
    )
    
class AppInfoMap(pa.DataFrameModel):
    app_name: Series[str] = pa.Field()
    image: Series[str] = pa.Field()
    category: Series[str] = pa.Field()