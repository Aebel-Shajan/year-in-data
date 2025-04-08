import Barplot from "./Barplot";


interface TimeSeriesData {
  date: string, 
  value: number
}


const WeeklyBarPlot = (
  {
    width,
    height,
    data
  }: {
    width: number,
    height: number,
    data: {date: string, value: number}[]
  }
) => {
  return (
    <Barplot 
      width={width}
      height={height}
      data={convertDateToWeekDay(data)}
    />
  );
}
 


function convertDateToWeekDay(data: TimeSeriesData[]) {
  return data.map(row => {
    const date = new Date(row.date);
    const weekDay = date.toLocaleString('en-US', { weekday: 'long' });
    return {
      name: weekDay,
      value: row.value
    };
  });
}



export default WeeklyBarPlot;