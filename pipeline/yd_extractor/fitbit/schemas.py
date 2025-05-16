import pandera as pa
from pandera.typing.pandas import DataFrame, Series


class RawTimeSeriesData(pa.DataFrameModel):
    class Config:
        coerce = True

    date: Series[str] = pa.Field(
        alias="dateTime",
    )
    value: Series[float] = pa.Field()


class TimeSeriesData(pa.DataFrameModel):
    date: Series[pa.Timestamp] = pa.Field(
        metadata={
            "tag": "date_column",
        }
    )
    value: Series[float] = pa.Field(
        metadata={
            "tag": "value_column",
            "units": "units",
        }
    )


class RawFitbitSleep(pa.DataFrameModel):
    class Config:
        coerce = True

    logId: Series[int] = pa.Field()
    dateOfSleep: Series[pa.Timestamp] = pa.Field()
    startTime: Series[str] = pa.Field()
    endTime: Series[str] = pa.Field()
    duration: Series[int] = pa.Field()
    minutesToFallAsleep: Series[int] = pa.Field()
    minutesAsleep: Series[int] = pa.Field()
    minutesAwake: Series[int] = pa.Field()
    minutesAfterWakeup: Series[int] = pa.Field()
    timeInBed: Series[int] = pa.Field()
    efficiency: Series[int] = pa.Field()


class FitbitSleep(pa.DataFrameModel):
    date: Series[pa.DateTime] = pa.Field(
        metadata={
            "tag": "date_column",
        },
    )
    start_time: Series[object] = pa.Field(
        metadata={
            "tag": "time_column",
        },
    )
    end_time: Series[object] = pa.Field(
        metadata={
            "tag": "time_column",
        }
    )
    total_sleep_hours: Series[float] = pa.Field(
        metadata={
            "tag": "value_column",
            "units": "hours",
        }
    )


class RawFitbitExercise(pa.DataFrameModel):
    class Config:
        coerce = True

    activityName: Series[str] = pa.Field()
    averageHeartRate: Series[int] = pa.Field(
        nullable=True,
        default=0,
    )
    calories: Series[int] = pa.Field()
    distance: Series[float] = pa.Field(
        nullable=True,
    )
    activeDuration: Series[int] = pa.Field()
    startTime: Series[str] = pa.Field()
    pace: Series[float] = pa.Field(
        nullable=True,
    )


class FitbitExercise(pa.DataFrameModel):
    activity_name: Series[str] = pa.Field(
        metadata={
            "tag": "category_column",
        }
    )
    average_heart_rate_bpm: Series[int] = pa.Field(
        metadata={
            "tag": "value_column",
        }
    )
    calories: Series[int] = pa.Field(
        metadata={
            "tag": "value_column",
            "units": "calories",            
        }
    )
    distance_km: Series[float] = pa.Field(
        metadata={
            "tag": "value_column",
            "units": "km",
        }
    )
    active_duration_minutes: Series[int] = pa.Field(
        metadata={
            "tag": "value_column",
            "units": "minutes",
        }
    )
    start_time: Series[object] = pa.Field(
        metadata={
            "tag": "time_column",
        }
    )
    pace_minutes_per_km: Series[float] = pa.Field(
        metadata={
            "tag": "value_column",
            "units": "minutes per km",
        }
    )
