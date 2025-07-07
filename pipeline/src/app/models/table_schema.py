
from typing import Any, Optional
from pydantic import BaseModel


class ValueColumn(BaseModel):
    name: str
    units: str
    range: tuple[float, float]
    
class CategoryColumn(BaseModel):
    name: str
    # ordered_distinct_categories: list[str]
    image_column: Optional[str]
    # link_column: Optional[str]

class TableSchema(BaseModel):
    datetime_column: str
    value_columns: dict[str, ValueColumn]
    category_columns: dict[str, CategoryColumn]


class TableEventRecords(BaseModel):
    schema: TableSchema
    records: list[dict[str, Any]]