import Barplot from "./Barplot";


interface TimeSeriesData {
  date: string, 
  value: number,
}


const DateBarPlot = (
  {
    width,
    height,
    data,
    group="month"
  }: {
    width: number,
    height: number,
    data: {date: string, value: number}[],
    group?: "month" | "weekday" 
  }
) => {
  return (
    <Barplot 
      width={width}
      height={height}
      data={group=="weekday" ? convertDateToWeekDay(data) : convertDateToMonth(data)}
      sort={false}
    />
  );
}
 

function convertDateToWeekDay(data: TimeSeriesData[]) {
  const weekDayOrder = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
  
  const groupedData = weekDayOrder.map(weekDay => {
    const matchingData = data.filter(row => {
      const date = new Date(row.date);
      return date.toLocaleString('en-US', { weekday: 'long' }) === weekDay;
    });
    return {
      name: weekDay,
      value: matchingData.reduce((sum, row) => sum + row.value, 0)
    };
  });

  return groupedData;
}

function convertDateToMonth(data: TimeSeriesData[]) {
  const monthOrder = [
    "January", "February", "March", "April", "May", "June", 
    "July", "August", "September", "October", "November", "December"
  ];

  const groupedData = monthOrder.map(month => {
    const matchingData = data.filter(row => {
      const date = new Date(row.date);
      return date.toLocaleString('en-US', { month: 'long' }) === month;
    });
    return {
      name: month,
      value: matchingData.reduce((sum, row) => sum + row.value, 0)
    };
  });

  return groupedData;
}




export default DateBarPlot;