import type { InputHeatmapData } from "./components/visualisations/heatmap-visual";
import type { Tree } from "./components/visualisations/treemap";



function getUTCDateOnly(dateStr: string): Date {
  const date = new Date(dateStr);
  return new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()));
}


interface DateMapDataType {
  [date: string]: number
}


/**
 * so simple in sql so hard in ts 😮‍💨
 * 
 * SELECT dateTimeCol, SUM(valueCol), CONCAT(SUM(valueCol), " ${units}"
 * FROM DATA
 * GROUP BY date(dateTimeCol);
 */
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


/**
 * SELECT categoryCol, SUM(valueCol) FROM data 
 * GROUP BY categoryCol
 */
export function prepareTreeMapData(
  fullData: Record<string, string|number>[],
  categoryCol: string,
  valueCol: string,
) {
  // const groupedData = Object.groupBy only in es2024 rip
   const groupedDataMap = fullData.reduce((dataMap: {[category: string]: number}, row) => {
      const category = row[categoryCol]
      const value = row[valueCol] as number
      if (!category || !value) return dataMap
      if (!dataMap[category]) {
        dataMap[category] = 0 as number
      }
      dataMap[category] += value
      return dataMap
    }, {} as {[category: string]: number})

    const flattenedGroupedData = Object.entries(groupedDataMap).map(([role, value])=> {
      return {
        type: "leaf",
        name: role,
        value: value as number
      }
    })
    const treeData: Tree = {
      type: "node",
      name: "no data to display!",
      value: 0,
      children: flattenedGroupedData.sort((a, b) => b.value - a.value) as Tree[]
    }
    return treeData
}