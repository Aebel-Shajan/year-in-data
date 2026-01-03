import { useEffect, useState } from 'react'
import { Button } from './components/ui/button'
import DarkModeToggle from './components/dark-mode-toggle'
import { HeatmapVisual } from './components/heatmap-visual'


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





  return (
    <>
      <div className='w-full h-full bg-slate-500 flex p-3 gap-2'>
        <div className='w-50 h-full flex flex-col gap-3 bg-background rounded-xl p-3'>
          <DarkModeToggle />
          <Button variant="outline" onClick={() => extractScreenTime()}>
            extract screen time
          </Button>
        </div>
        <div className='min-h-full flex-1 bg-background rounded-xl overflow-x-hidden p-3'>
          <div className='p-2 outline rounded-xl overflow-scroll'>
            <HeatmapVisual data={data} />
          </div>
        </div>
      </div>

    </>
  )
}

export default App
