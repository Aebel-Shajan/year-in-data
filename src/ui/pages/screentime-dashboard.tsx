import { Button } from "@/components/ui/button";
import { HeatmapVisual } from "@/components/visualisations/heatmap-visual";
import MonthlyBarChart from "@/components/visualisations/montthly-barchart";
import { Treemap, type Tree } from "@/components/visualisations/treemap";
import * as d3 from "d3";
import { useEffect, useState } from "react";



export default function ScreenTimeDashboard() {

  const [data, setData] = useState<any[]>([])

  async function fetchScreenTimeByYear(year: number) {
    const records = await window.electronAPI.getScreenTimeByYear(year)
    // console.log(`Screen time for ${year}:`, records);
    return records;
  }

  async function extractScreenTime() {
    await window.electronAPI.extractScreenTime()
    fetchScreenTimeByYear(2025).then(newData => setData(newData))
  }

  useEffect(() => {
    fetchScreenTimeByYear(2025).then(newData => setData(newData))
  }, [])


  const groupedByUsageMap = d3.rollup(
    data,
    v => d3.sum(v, d => d["usage"]),
    d => d["app"]
  )
  const flattenedList = Array.from(groupedByUsageMap).map(([app, usage]) => {
    return { app, usage }
  })
  const treeData: Tree = {
    type: "node",
    name: "boss",
    value: 0,
    children: flattenedList.sort((a, b) => b.usage - a.usage).map(row => {
      return {
        type: "leaf",
        name: row["app"],
        value: row["usage"]
      }
    })
  }

  const groupedByMonthMap = d3.rollup(
    data,
    v => d3.sum(v, d => d["usage"]),
    d => {
      return (new Date(d["start_time"])).toLocaleString("en-US", { month: "short" })
    }
  )
  const shortMonthNames = [
    "Jan", "Feb", "Mar", "Apr",
    "May", "Jun", "Jul", "Aug",
    "Sep", "Oct", "Nov", "Dec"
  ];
  const flattenedMonthList = shortMonthNames.map((month) => {
    let value = groupedByMonthMap.get(month)
    if (value == undefined) {
      value = 0
    }
    return {
      month,
      value
    }
  })
  console.log(flattenedMonthList)

  return (
    <div className=' w-full h-fit p-3 flex flex-col gap-3'>

      <div className='p-3 outline rounded-xl flex items-center justify-between sticky top-3 bg-background'>
        <div className='font-extrabold text-2xl'>
          Screen time
        </div>
        <div className='flex'>

          <Button variant="outline" onClick={() => extractScreenTime()}>
            extract screen time
          </Button>
        </div>
      </div>

      <div className='p-2 outline rounded-xl overflow-scroll h-50'>
        <HeatmapVisual data={data} />
      </div>

      <div className='p-2 outline rounded-xl overflow-scroll flex justify-center h-80'>
        <Treemap data={treeData} width={600} height={300} />
      </div>

      <div className='p-2 outline rounded-xl overflow-scroll flex justify-center'>
        <MonthlyBarChart data={flattenedMonthList} />
      </div>
    </div>
  )
}