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
   const groupedDataMap = fullData.reduce((dataMap:DateMapDataType, row) => {
      const category = row[categoryCol]
      const value = row[valueCol] as number
      if (!category || !value) return dataMap
      if (!dataMap[category]) {
        dataMap[category] = 0 as number
      }
      dataMap[category] += value
      return dataMap
    }, {} as DateMapDataType)

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


/**
 * SELECT 
 * TO_CHAR(TO_DATE(EXTRACT(MONTH FROM dateTimeCol)::TEXT, 'MM'), 'Mon') AS month,
 * SUM(valueCol) AS value
 * FROM my_table
 * WHERE dateTimeCol IS NOT NULL
 * GROUP BY EXTRACT(MONTH FROM dateTimeCol)
 * ORDER BY EXTRACT(MONTH FROM dateTimeCol);
 */

export function prepareMonthlyGroupedData(
  fullData: Record<string, string|number>[],
  dateTimeCol: string,
  valueCol: string
) {

    const shortMonthNames = [
      "Jan", "Feb", "Mar", "Apr",
      "May", "Jun", "Jul", "Aug",
      "Sep", "Oct", "Nov", "Dec"
    ];
    const initialMonthNameMap = Object.fromEntries(shortMonthNames.map(month => [month, 0]))
    const groupedDataMap = fullData.reduce((dataMap: DateMapDataType, row) => {
      const dateTime = row[dateTimeCol]
      const value = row[valueCol] as number
      if (!dateTime || !value) return dataMap
      const month = new Date(dateTime).toLocaleString("en-US", { month: "short" })
      if (!dataMap[month]) {
        dataMap[month] = 0 as number
      }
      dataMap[month] += value
      return dataMap
    }, initialMonthNameMap as DateMapDataType)


    const flattenedGroupedData = Object.entries(groupedDataMap).map(([month, value])=> {
      return {
        month: month,
        value: value as number
      }
    })
    return flattenedGroupedData
}