import { Button } from "@/components/ui/button";
import { HeatmapVisual } from "@/components/visualisations/heatmap-visual";
import MonthlyBarChart from "@/components/visualisations/montthly-barchart";
import { Treemap } from "@/components/visualisations/treemap";
import { prepareHeatmapData, prepareMonthlyGroupedData, prepareTreeMapData } from "@/utils";
import { useEffect, useState } from "react";


export default function ZshHistoryCommandsDashboard() {
  const table_name = "zsh_history_commands"
  const [data, setData] = useState<any[]>([])

  useEffect(() => {
    fetchData(2025)
  }, [])

  
  async function fetchData(year: number) {
    const records = await window.electronAPI.getDataByYear(table_name, year, "datetime")
    setData(records)
    console.log(`rows for ${table_name} ${year}:`, records.length);
    return records;
  }

  async function runEtl() {
    const response = await window.electronAPI.runEtl(table_name, {})
    if (!response.success) {
      console.log(`Failed to run etl for ${table_name}`)
    }

    await fetchData(2025)
  }


  const heatmapData = prepareHeatmapData(
    data,
    "datetime",
    "count",
    "commands"
  )

  const treemapData = prepareTreeMapData(
    data,
    "command",
    "count"
  )

  const dataGroupedByMonth = prepareMonthlyGroupedData(
    data,
    "datetime",
    "count"
  )

  return (
    <div className=' w-full h-fit p-3 flex flex-col gap-3'>

      <div className='p-3 outline rounded-xl flex items-center justify-between sticky top-3 bg-background'>
        <div className='font-extrabold text-2xl'>
          Zsh command history
        </div>

        <div className='flex'>

          <Button variant={"outline"} onClick={runEtl}>
            Extract zsh history data
          </Button>

        </div>
      </div>

      <div className='p-2 outline rounded-xl overflow-scroll h-50'>
        <HeatmapVisual data={heatmapData} range={[0, 100]} />
      </div>

      <div className='p-2 outline rounded-xl overflow-scroll h-50'>
        <Treemap data={treemapData} />
      </div>

      <div className='p-2 outline rounded-xl overflow-scroll flex justify-center'>
        <MonthlyBarChart data={dataGroupedByMonth} />
      </div>


      <div className="font-light font-mono text-sm flex-1 wrap-break-word w-full bg-accent p-2 rounded-md">
        {JSON.stringify(data.slice(0, 10))}
      </div>
    </div>
  )
}