from pandera.typing.pandas import DataFrame, Series
import pandera as pa


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