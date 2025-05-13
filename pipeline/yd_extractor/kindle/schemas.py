import datetime

import pandera as pa
from pandera.typing.pandas import Series


def check_is_valid_asin(asin: str) -> bool:
    return len(asin) == 10 and asin.isalnum() and asin.isupper()


class RawAsinMap(pa.DataFrameModel):
    class Config:
        coerce = True

    asin: Series[str] = pa.Field(nullable=False)
    product_name: Series[str] = pa.Field(nullable=False)
    purchase_date: Series[pa.DateTime] = pa.Field(nullable=False)


class AsinMap(pa.DataFrameModel):
    asin: Series[str] = pa.Field(
        nullable=False,
        unique=True,
    )
    product_name: Series[str] = pa.Field(
        nullable=False,
        unique=True,
    )

    @pa.check("asin")
    def is_valid_asin(self, series: Series[str]) -> Series[bool]:
        return series.apply(check_is_valid_asin)


class RawKindleReading(pa.DataFrameModel):
    class Config:
        coerce = True

    asin: Series[str] = pa.Field(
        nullable=True,
        alias="ASIN",
        default="",
    )
    start_timestamp: Series[str] = pa.Field(nullable=True)
    total_reading_millis: Series[int] = pa.Field(
        nullable=True,
        default=0,
    )
    number_of_page_flips: Series[int] = pa.Field(
        nullable=False,
        default=0,
    )


class KindleReading(pa.DataFrameModel):
    date: Series[pa.Date] = pa.Field(
        nullable=False,
        metadata={
            "tag": "date_column",
        },
    )
    start_time: Series[object] = pa.Field(
        nullable=False,
        metadata={
            "tag": "date_column",
        },
    )
    asin: Series[str] = pa.Field(
        nullable=False,
        metadata={
            "tag": "",
        },
    )
    book_name: Series[str] = pa.Field(
        nullable=True,
        metadata={
            "tag": "category_column",
        },
    )
    total_reading_minutes: Series[int] = pa.Field(
        nullable=False,
        metadata={
            "tag": "value_column",
        },
    )
    image: Series[str] = pa.Field(
        nullable=False,
        metadata={
            "tag": "image_column",
        },
    )
    number_of_page_flips: Series[int] = pa.Field(
        nullable=False,
        metadata={
            "tag": "value_column",
        },
    )

    @pa.check("asin")
    def is_valid_asin(self, series: Series[str]) -> Series[bool]:
        return series.apply(check_is_valid_asin)

    @pa.check("start_time")
    def is_time(self, series: Series[object]) -> Series[bool]:
        return series.apply(lambda x: isinstance(x, datetime.time))
