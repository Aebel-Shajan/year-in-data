import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { HeatmapVisual } from "@/components/visualisations/heatmap-visual";
import { Treemap, type Tree } from "@/components/visualisations/treemap";
import { prepareHeatmapData } from "@/utils";
import { useEffect, useState } from "react";


export default function ChatGptMessageDashboard() {
  const table_name = "chat_gpt_messages"
  const [filePath, setFilePath] = useState<string | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false);
  const [data, setData] = useState<any[]>([])

  useEffect(() => {
    fetchData(2025)
  }, [])


  function clearSelectedFilePath() {
    setFilePath(null)
  }

  async function selectZipFile() {
    const path = await window.electronAPI.selectFile()
    if (!path) return
    setFilePath(path)
  }

  async function fetchData(year: number) {
    const records = await window.electronAPI.getDataByYear(table_name, year, "datetime")
    setData(records)
    console.log(`rows for ${table_name} ${year}:`, records.length);
    return records;
  }

  async function runEtl() {
    if (!filePath) {
      console.log("Failed to run chatgpt pipeline")
      return
    } // create method in electron api to dialog this
    const response = await window.electronAPI.runEtl(table_name, { zipPath: filePath, targetDir: "./data/chatgpt" })
    if (!response.success) {
      console.log(`Failed to run etl for ${table_name}`)
    }
    await fetchData(2025)
    setDialogOpen(false)
  }

  const heatmapData = prepareHeatmapData(
    data.map(row => {
      row.value = 1
      return row
    }),
    "datetime",
    "value",
    "messages"
  )

  const groupedDataMap = data.reduce((dataMap, row) => {
    const role = row["role"]
    if (!role) return dataMap
    if (!dataMap[role]) {
      dataMap[role] = 0
    }
    dataMap[role] += 1
    return dataMap
  }, {})
  const flattenedGroupedData = Object.entries(groupedDataMap).map(([role, value])=> {
    return {
      type: "leaf",
      name: role,
      value: value as number
    }
  })
  const treeData: Tree = {
    type: "node",
    name: "boss",
    value: 0,
    children: flattenedGroupedData.sort((a, b) => b.value - a.value) as Tree[]
  }

  return (
    <div className=' w-full h-fit p-3 flex flex-col gap-3'>

      <div className='p-3 outline rounded-xl flex items-center justify-between sticky top-3 bg-background'>
        <div className='font-extrabold text-2xl'>
          ChatGpt messages
        </div>

        <div className='flex'>
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button variant={"outline"} onClick={clearSelectedFilePath}>
                Extract chatgpt data
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Extract chatgpt data</DialogTitle>

                <DialogDescription>
                  Select the chatgpt zip file you would like to process.
                </DialogDescription>
              </DialogHeader>
              <div className="flex w-full gap-1">
                <Button variant="outline" onClick={selectZipFile}>
                  Select file
                </Button>
                {filePath &&
                  <div className="font-light font-mono text-sm flex-1 wrap-break-word w-64 bg-accent p-2 rounded-md">
                    {filePath}
                  </div>
                }
              </div>
              {filePath &&
                <Button className="w-fit" onClick={runEtl}>
                  Extract chatgpt message data
                </Button>
              }


            </DialogContent>
          </Dialog>

        </div>
      </div>

      <div className='p-2 outline rounded-xl overflow-scroll h-50'>
        <HeatmapVisual data={heatmapData} range={[0, 100]}/>
      </div>
      <div className='p-2 outline rounded-xl overflow-scroll h-50'>
        <Treemap data={treeData} />
      </div>


      <div className="font-light font-mono text-sm flex-1 wrap-break-word w-full bg-accent p-2 rounded-md">

        {JSON.stringify(data.slice(0, 10))}
      </div>
    </div>
  )
}