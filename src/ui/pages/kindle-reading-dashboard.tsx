import { Button } from "@/components/ui/button";
import { HeatmapVisual } from "@/components/visualisations/heatmap-visual";
import BarChartVisual from "@/components/visualisations/barchart-visual";
import { Treemap } from "@/components/visualisations/treemap";
import { prepareHeatmapData, prepareHourlyGroupedData, prepareMonthlyGroupedData, prepareTreeMapData } from "@/utils";
import { useEffect, useState } from "react";
import { EtlRunModal } from "@/components/etl/EtlRunModal";


export default function KindleReadingDashboard({selectedYear}: {selectedYear: number}) {
  const table_name = "kindle_reading_sessions"
  const [data, setData] = useState<any[]>([])
  const [booksCompleted, setBooksCompleted] = useState<any[]>([])

  useEffect(() => {
    fetchData(selectedYear)
    fetchBooksCompleted(selectedYear)
  }, [selectedYear])

  async function fetchData(year: number) {
    const records = await window.electronAPI.getDataByYear(table_name, year, "datetime")
    setData(records)
    console.log(`rows for ${table_name} ${year}:`, records.length);
    return records;
  }

  async function fetchBooksCompleted(year: number) {
    const records = await window.electronAPI.getDataByYear("kindle_books_completed", year, "datetime")
    setBooksCompleted(records)
    console.log(`rows for kindle_books_completed ${year}:`, records.length);
    return records;
  }

  // convert ms to minutes for display
  const dataWithMinutes = data.map(row => ({
    ...row,
    value: Number(row.total_reading_ms) / 60000
  }))

  const heatmapData = prepareHeatmapData(
    dataWithMinutes,
    "datetime",
    "value",
    "minutes"
  )

  const treemapData = prepareTreeMapData(
    dataWithMinutes,
    "product_name",
    "value"
  )

  const dataGroupedByMonth = prepareMonthlyGroupedData(
    dataWithMinutes,
    "datetime",
    "value"
  )

  const dataGroupedByHour = prepareHourlyGroupedData(
    dataWithMinutes,
    "datetime",
    "value"
  )

  const totalHours = data.reduce((sum, row) => sum + Number(row.total_reading_ms), 0) / 3600000

  return (
    <div className=' w-full h-fit p-3 flex flex-col gap-3'>

      <div className='p-3 outline rounded-xl flex items-center justify-between sticky top-3 bg-background'>
        <div className='font-extrabold text-2xl'>
          Kindle reading
        </div>

        <div className='flex gap-2 items-center'>
          <div className="text-sm font-mono text-muted-foreground">
            {totalHours.toFixed(1)}h total | {booksCompleted.length} books completed
          </div>
          <div className='flex'>
            <EtlRunModal
              tableName={table_name}
              label="Kindle Reading"
              requiresFile={true}
              targetDir="./data/kindle"
              onComplete={() => fetchData(selectedYear)}
              trigger={<Button variant="outline">Extract Kindle data</Button>}
            />
          </div>
        </div>
      </div>

      <div className='p-4 outline rounded-xl overflow-scroll h-fit'>
        <HeatmapVisual data={heatmapData} range={[0, 120]} year={selectedYear} />
      </div>

      <div className='p-2 outline rounded-xl overflow-scroll h-50'>
        <Treemap data={treemapData} />
      </div>

      <div className="w-full flex flex-wrap gap-3">
        <div className='p-2 outline rounded-xl overflow-scroll flex justify-center grow'>
          <BarChartVisual data={dataGroupedByMonth} xCol="month" yCol="value" />
        </div>

        <div className='p-2 outline rounded-xl overflow-scroll flex justify-center grow'>
          <BarChartVisual data={dataGroupedByHour} xCol="hour" yCol="value" />
        </div>
      </div>

      {booksCompleted.length > 0 &&
        <div className='p-4 outline rounded-xl'>
          <div className='font-bold text-lg mb-2'>Books completed</div>
          <div className="flex flex-col gap-1">
            {booksCompleted.map((book: any, i: number) => (
              <div key={i} className="flex justify-between font-mono text-sm p-1 rounded hover:bg-accent">
                <span>{book.product_name}</span>
                <span className="text-muted-foreground">{book.completed_date}</span>
              </div>
            ))}
          </div>
        </div>
      }

      <div className="font-light font-mono text-sm flex-1 wrap-break-word w-full bg-accent p-2 rounded-md">
        {JSON.stringify(data.slice(0, 10))}
      </div>
    </div>
  )
}
