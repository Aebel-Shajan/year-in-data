import { Button } from "@/components/ui/button";
import { EtlRunModal } from "@/components/etl/EtlRunModal";
import { HeatmapVisual } from "@/components/visualisations/heatmap-visual";
import BarChartVisual from "@/components/visualisations/barchart-visual";
import { Treemap } from "@/components/visualisations/treemap";
import { prepareHeatmapData, prepareHourlyGroupedData, prepareMonthlyGroupedData, prepareTreeMapData } from "@/utils";
import { useEffect, useState } from "react";


export default function ChatGptMessageDashboard({selectedYear}: {selectedYear: number}) {
  const table_name = "chat_gpt_messages"
  const [data, setData] = useState<any[]>([])

  useEffect(() => {
    fetchData(selectedYear)
  }, [selectedYear])

  async function fetchData(year: number) {
    const records = await window.electronAPI.getDataByYear(table_name, year, "datetime")
    setData(records)
    console.log(`rows for ${table_name} ${year}:`, records.length);
    return records;
  }

  const dataWithValueCount = data.map(row => {
    row.value = 1
    return row
  })
  const heatmapData = prepareHeatmapData(
    dataWithValueCount,
    "datetime",
    "value",
    "messages"
  )

  const treemapData = prepareTreeMapData(
    dataWithValueCount,
    "role",
    "value"
  )

  const dataGroupedByMonth = prepareMonthlyGroupedData(
    dataWithValueCount,
    "datetime",
    "value"
  )

  const dataGroupedByHour = prepareHourlyGroupedData(
    dataWithValueCount,
    "datetime",
    "value"
  )

  return (
    <div className=' w-full h-fit p-3 flex flex-col gap-3'>

      <div className='p-3 outline rounded-xl flex items-center justify-between sticky top-3 bg-background'>
        <div className='font-extrabold text-2xl'>
          ChatGpt messages
        </div>

        <div className='flex'>
          <EtlRunModal
            tableName="chat_gpt_messages"
            label="ChatGPT Messages"
            requiresFile={true}
            targetDir="./data/chatgpt"
            onComplete={() => fetchData(selectedYear)}
            trigger={<Button variant="outline">Extract chatgpt data</Button>}
          />
        </div>
      </div>

      <div className='p-4 outline rounded-xl overflow-scroll h-fit'>
        <HeatmapVisual data={heatmapData} range={[0, 100]} year={selectedYear}/>
      </div>

      <div className='p-2 outline rounded-xl overflow-scroll h-50'>
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


      <div className="font-light font-mono text-sm flex-1 wrap-break-word w-full bg-accent p-2 rounded-md">
        {JSON.stringify(data.slice(0, 10))}
      </div>
    </div>
  )
}