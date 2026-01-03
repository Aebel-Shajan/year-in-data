import { useEffect, useState } from 'react'
import { Button } from './components/ui/button'
import DarkModeToggle from './components/dark-mode-toggle'
import { HeatmapVisual } from './components/visualisations/heatmap-visual'
import * as d3 from 'd3'
import { Treemap } from './components/visualisations/treemap'


function App() {
  const [data, setData] = useState([])

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
    return {app, usage}
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



  return (
    <>
      <div className='w-full h-full bg-slate-500 flex p-3 gap-2'>
        <div className='w-50 h-full flex flex-col gap-3 bg-background rounded-xl p-3'>
          <DarkModeToggle />

        </div>
        <div className='min-h-full flex-1 bg-background rounded-xl overflow-x-hidden p-3 flex flex-col gap-3'>
          <div className='p-3 outline rounded-xl overflow-scroll flex items-center justify-between'>
            <div className='font-extrabold text-2xl'>
              Screen time
            </div>
            <div className='flex'>

          <Button variant="outline" onClick={() => extractScreenTime()}>
            extract screen time
          </Button>
            </div>
          </div>

          <div className='p-2 outline rounded-xl overflow-scroll'>
            <HeatmapVisual data={data} />
          </div>

          <div className='p-2 outline rounded-xl overflow-scroll flex justify-center'>
            <Treemap data={treeData} width={600} height={300} />
          </div>

        </div>
      </div>

    </>
  )
}

export default App
