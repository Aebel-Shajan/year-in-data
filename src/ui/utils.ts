import type { InputHeatmapData } from "./components/visualisations/heatmap-visual";



function getUTCDateOnly(dateStr: string): Date {
  const date = new Date(dateStr);
  return new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()));
}


interface DateMapDataType {
  [date: string]: number
}


export function prepareHeatmapData(
  fullData: Record<string, string | number>[],
  dateTimeCol: string,
  valueCol: string,
  units: string = ""
): InputHeatmapData[] {
  const dateValueMap: DateMapDataType = fullData
    .map((row: Record<string, string | number>) => ({
      date: getUTCDateOnly(row[dateTimeCol] as string).toDateString(), // "YYYY-MM-DD"
      value: row[valueCol],
    }))
    .reduce((dateMap, row) => {
      if (!dateMap[row.date]) {
        dateMap[row.date] = 0
      }
      dateMap[row.date] += row.value as number
      return dateMap
    }, {} as DateMapDataType)

  const listOfRows = Object.entries(dateValueMap).map(([date, value]) => {
    return {
      date,
      value,
      label: `${value} ${units}`
    }
  })
  return listOfRows
}

export function constructDurationString(timeInSeconds: number): string {
  const hours = Math.floor(timeInSeconds / 3600)
  const minutes = Math.floor((timeInSeconds % 3600) / 60)
  return `${hours}h ${minutes}m`
}