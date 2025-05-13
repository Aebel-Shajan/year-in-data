import pandera as pa
from pandera.typing.pandas import Series

def check_is_valid_asin(asin: str) -> bool:
    return (
        len(asin) == 10 and
        asin.isalnum() and
        asin.isupper()
    )

class RawAsinMap(pa.DataFrameModel):
    class Config:
        coerce=True
    asin: Series[str] = pa.Field(nullable=False)
    product_name: Series[str] = pa.Field(nullable=False)
    purchase_date: Series[pa.DateTime] = pa.Field(nullable=False)


class AsinMap(pa.DataFrameModel):
    class Config:
        coerce=False
    
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

    