import { Button } from "@/components/ui/button";
import { EtlRunModal } from "@/components/etl/EtlRunModal";
import { HeatmapVisual } from "@/components/visualisations/heatmap-visual";
import BarChartVisual from "../components/visualisations/barchart-visual.tsx";
import { Treemap } from "@/components/visualisations/treemap";
import { constructDurationString, prepareHeatmapData, prepareHourlyGroupedData, prepareMonthlyGroupedData, prepareTreeMapData } from "@/utils";

import { useEffect, useState } from "react";



export default function ScreenTimeDashboard({selectedYear}: {selectedYear: number}) {
  const [data, setData] = useState<any[]>([])
  const table_name = "screen_time"


  async function fetchScreenTimeByYear(year: number) {
    const records = await window.electronAPI.getDataByYear(table_name, year, "start_time")
    // console.log(`Screen time for ${year}:`, records);
    setData(records)
  }

  useEffect(() => {
    fetchScreenTimeByYear(selectedYear)
  }, [selectedYear])


  const treemapData = prepareTreeMapData(
    data,
    "app",
    "usage"
  )
  
  let heatmapData = prepareHeatmapData(
    data,
    "start_time",
    "usage",
    ""
  ).map(row => {
    row.label = constructDurationString(row.value)
    return row
  })

  const dataGroupedByMonth = prepareMonthlyGroupedData(
    data,
    "start_time",
    "usage"
  )

  const dataGroupedByHour = prepareHourlyGroupedData(
    data,
    "start_time",
    "usage"
  )


  return (
    <div className=' w-full h-fit p-3 flex flex-col gap-3'>

      <div className='p-3 outline rounded-xl flex items-center justify-between sticky top-3 bg-background'>
        <div className='font-extrabold text-2xl'>
          Screen time
        </div>
        <div className='flex'>
          <EtlRunModal
            tableName="screen_time"
            label="Screen Time"
            requiresFile={false}
            onComplete={() => fetchScreenTimeByYear(selectedYear)}
            trigger={<Button variant="outline">extract screen time</Button>}
          />
        </div>
      </div>

      <div className='p-2 outline rounded-xl overflow-scroll h-fit'>
        <HeatmapVisual data={heatmapData} range={[0, 10 * 3600]} year={selectedYear}  />
      </div>

      <div className='p-2 outline rounded-xl overflow-scroll flex justify-center h-80'>
        <Treemap data={treemapData} />
      </div>

      <div className="w-full flex flex-wrap gap-3">
 
       <div className='p-2 outline rounded-xl overflow-scroll flex justify-center  grow'>
         <BarChartVisual data={dataGroupedByMonth} xCol="month" yCol="value" />
       </div>
 
       <div className='p-2 outline rounded-xl overflow-scroll flex justify-center grow'>
         <BarChartVisual data={dataGroupedByHour} xCol="hour" yCol="value" />
       </div>
       </div>
    </div>
  )
}