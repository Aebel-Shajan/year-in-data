import { Button } from "@/components/ui/button";
import { HeatmapVisual } from "@/components/visualisations/heatmap-visual";
import BarChartVisual from "@/components/visualisations/barchart-visual";
import { Treemap } from "@/components/visualisations/treemap";
import { prepareCategoryGroupedData, prepareHeatmapData, prepareMonthlyGroupedData, prepareTreeMapData } from "@/utils";
import { useEffect, useState } from "react";
import { EtlRunModal } from "@/components/etl/EtlRunModal";


export default function HsbcTransactionsDashboard({selectedYear}: {selectedYear: number}) {
  const table_name = "hsbc_transactions"
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


  function mapDetail(detailString: string | undefined) {
    if (detailString === undefined) {
      return "unknown"
    }
    const detailMap = {

      "amazon": "amazon",
      "barber": "barber",
      // "transfer": "bank_transfer",
      "uber": "uber",
      "freetrade": "freetrade",
      "shajan": "family",
      "spotify": "sportify",
      "transfer": "savings",
      "saver": "savings",
      "carsa": "carsa",
      "babu": "cousins",
      "nintendo": "nintendo",
      "claude": "ai",
      "openai": "ai",
      "trainline": "trainline",
      "netflix": "netflix",
      "mcdonalds": "mcdonalds",
      "google": "google",
      "revolut": "revolut",
      "greggs": "greggs",
      "linkedin": "linkedin",
      "currys": "currys",
      "morrisons": "morrisons",
      "bee network": "beenetwork",
      "beenetwork": "beenetwork",
      "steam": "steam",
      "stagecoach": "stagecoach",
      "gym": "gym",
      "lebara": "lebara",
      "proton": "proton",
      "london": "london",
      "sheffield": "sheffield",
      "bolton": "bolton",
      "salford": "manchester",
      "hyde": "manchester",
      "manchester": "manchester",
      "m'ster": "manchester",
      "manc": "manchester",
    }
    const detailEntries = Object.entries(detailMap)
    for (let i = 0; i < detailEntries.length; i++) {
      const [key, value] = detailEntries[i]
      if (detailString.toLowerCase().includes(key)) {
        console.log(value)
        return value
      }
    }
    return detailString
  }

  const sortedData = data.map(row => {
    return {
      ...row,
      "category": mapDetail(row["details"])
    }
  })
  const groupedByCategory = prepareCategoryGroupedData(sortedData, "category", "amount")


  const categoryGroupedExpenses = groupedByCategory.filter(row => row["value"] < 0).map(row => {
    return {
      ...row,
      "value": Math.abs(row["value"])
    }
  })

  const categoryGroupedIncome = groupedByCategory.filter(row => row["value"] > 0).map(row => {
    return {
      ...row,
      "value": Math.abs(row["value"])
    }
  })

  const expenses = sortedData.filter(row => row["amount"] < 0).map(row => {
    return {
      ...row,
      "amount": Math.abs(row["amount"])
    }
  })
  const income = sortedData.filter(row => row["amount"] > 0)


  const heatmapData = prepareHeatmapData(
    expenses,
    "date",
    "amount",
    "pounds"
  )

  const expensesTreemapData = prepareTreeMapData(
    categoryGroupedExpenses,
    "category",
    "value"
  )

  const incomeTreemapData = prepareTreeMapData(
    categoryGroupedIncome,
    "category",
    "value"
  )

  const dataGroupedByMonth = prepareMonthlyGroupedData(
    expenses,
    "date",
    "amount"
  )


  return (
    <div className=' w-full h-fit p-3 flex flex-col gap-3'>

      <div className='p-3 outline rounded-xl flex items-center justify-between sticky top-3 bg-background'>
        <div className='font-extrabold text-2xl'>
          Hsbc transactions
        </div>

        <div className='flex'>
        <div className='flex'>
          <EtlRunModal
            tableName={table_name}
            label="hsbc statements"
            requiresFile={true}
            targetDir="./data/hsbc"
            onComplete={() => fetchData(selectedYear)}
            trigger={<Button variant="outline">Extract hsbc statements</Button>}
          />
        </div>
        </div>
      </div>

      <div className='p-4 outline rounded-xl overflow-scroll h-fit'>
        <HeatmapVisual data={heatmapData} range={[0, 500]}  year={selectedYear} />
      </div>

      <div className='p-2 outline rounded-xl overflow-scroll h-fit'>
        <div className="flex justify-between">

          <h2 className="font-extrabold">Expenses: </h2>
          <div>
            {categoryGroupedExpenses.reduce((prev, current) => prev + current.value, 0).toFixed(2)}
          </div>
        </div>
        <div className="h-90 w-full">
          <Treemap data={expensesTreemapData} />
        </div>
      </div>
      <div className='p-2 outline rounded-xl overflow-scroll h-fit'>
        <div className="flex justify-between">

          <h2 className="font-extrabold">Income: </h2>
          <div>
            {categoryGroupedIncome.reduce((prev, current) => prev + current.value, 0).toFixed(2)}
          </div>
        </div>
        <div className="h-90 w-full">
          <Treemap data={incomeTreemapData} />
        </div>

      </div>

      <div className='p-2 outline rounded-xl overflow-scroll flex justify-center  grow h-80'>
        <BarChartVisual data={dataGroupedByMonth} xCol="month" yCol="value" />
      </div>





      <div className="font-light font-mono text-sm flex-1 wrap-break-word w-full bg-accent p-2 rounded-md">
        {JSON.stringify(data.slice(0, 10))}
      </div>
    </div>
  )
}