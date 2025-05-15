import datetime
from typing import Optional

import pandas as pd
import pandera as pa
from pandera.typing.pandas import Series


# Define schema for input data
class RawStrongWorkouts(pa.DataFrameModel):
    class Config:
        coerce = True

    # Workout info
    workout_number: Series[int] = pa.Field(
        alias="Workout #",
        nullable=False,
    )
    date: Series[pa.DateTime] = pa.Field(
        alias="Date",
        nullable=False,
    )
    workout_name: Series[str] = pa.Field(
        alias="Workout Name",
        nullable=True,
    )
    set_order: Series[str] = pa.Field(
        alias="Set Order",
        nullable=False,
    )
    workout_duration_seconds: Series[int] = pa.Field(
        alias="Duration (sec)",
        nullable=True,
    )
    workout_notes: Series[str] = pa.Field(
        alias="Workout Notes",
        nullable=True,
    )

    # Exercise specific info
    exercise_name: Series[str] = pa.Field(
        alias="Exercise Name",
        nullable=True,
    )
    weight: Series[float] = pa.Field(
        alias=r"^(Weight \(kg\)|Weight \(lb\))$",
        regex=True,
        nullable=True,
        ge=0,
    )

    reps: Series[int] = pa.Field(
        alias="Reps",
        nullable=False,
        default=0,
        ge=0,
    )
    rpe: Series[float] = pa.Field(
        alias="RPE",
        nullable=True,
        ge=0,
        le=10,
    )
    distance: Series[float] = pa.Field(
        alias=r"^(Distance|Distance \(meters\)|Distance \(miles\) )$",
        regex=True,
        nullable=True,
        ge=0,
    )
    seconds: Series[int] = pa.Field(
        alias="Seconds",
        ge=0,
        nullable=False,
        default=0,
    )
    notes: Series[str] = pa.Field(
        alias="Notes",
        nullable=True,
    )


# Define schema for output data
class StrongWorkouts(pa.DataFrameModel):
    workout_number: Series[int] = pa.Field(
        nullable=False,
        unique=True,
    )

    date: Series[pa.DateTime] = pa.Field(
        nullable=False,
        metadata={
            "tag": "date_column",
        },
    )
    start_time: Series[object] = pa.Field(
        nullable=False,
        metadata={
            "tag": "start_time_column",
        },
    )
    workout_name: Series[pa.Category] = pa.Field(
        nullable=False,
        metadata={
            "tag": "category_column",
        },
    )
    workout_duration_minutes: Series[int] = pa.Field(
        ge=0,
        nullable=False,
        metadata={
            "tag": "value_column",
            "units": "minutes",
        },
    )
    workout_volume: Series[int] = pa.Field(
        nullable=False,
        metadata={
            "tag": "value_column",
            "units": "kg",
        },
    )

    @pa.check("start_time")
    def is_time(self, series: Series[object]) -> Series[bool]:
        return series.apply(lambda x: isinstance(x, datetime.time))
