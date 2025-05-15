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
    date: Series[pa.Timestamp] = pa.Field()
    value: Series[float] = pa.Field()


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
    date: Series[pa.DateTime] = pa.Field()
    start_time: Series[object] = pa.Field()
    end_time: Series[object] = pa.Field()
    total_sleep_hours: Series[float] = pa.Field()


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
    activity_name: Series[str] = pa.Field()
    average_heart_rate_bpm: Series[int] = pa.Field()
    calories: Series[int] = pa.Field()
    distance_km: Series[float] = pa.Field()
    active_duration_minutes: Series[int] = pa.Field()
    start_time: Series[object] = pa.Field()
    pace_minutes_per_km: Series[float] = pa.Field()
