from typing import Optional

import pandera as pa
from pandera.typing.pandas import Series


class RawAppUsageScreenTime(pa.DataFrameModel):
    class Config:
        coerce = True

    app_name: Series[str] = pa.Field(
        alias="App name",
        nullable=True,
    )
    date: Series[str] = pa.Field(
        alias="Date",
        nullable=True,
    )
    time: Series[object] = pa.Field(
        alias="Time",
        nullable=True,
    )
    duration: Series[object] = pa.Field(
        alias="Duration",
        nullable=True,
    )


class AppUsageScreenTime(pa.DataFrameModel):
    app_name: Series[str] = pa.Field(
        metadata={
            "tag": "category_column",
        },
    )
    date: Series[pa.Timestamp] = pa.Field(
        metadata={
            "tag": "date_column",
        },
    )
    time: Series[object] = pa.Field(
        metadata={
            "tag": "time_column",
        },
    )
    duration_minutes: Series[int] = pa.Field(
        metadata={
            "tag": "value_column",
            "units": "minutes",
        }
    )
    image: Optional[Series[str]] = pa.Field(
        metadata={
            "tag": "image_column",
            "category": "app_name",
        },
    )
    category: Optional[Series[str]] = pa.Field(
        # metadata={ # TODO: Add in future
        #     "tag": "category_column",
        # }
    )


class RawAppInfoMap(pa.DataFrameModel):
    class Config:
        coerce = True

    app_name: Series[str] = pa.Field(
        alias="App name",
        nullable=True,
    )
    package_name: Series[str] = pa.Field(alias="Package name", nullable=True)
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
