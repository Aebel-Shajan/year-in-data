import { useState } from 'react'
import { Button } from './components/ui/button'
import DarkModeToggle from './components/dark-mode-toggle'
import { HeatmapVisual } from './components/heatmap-visual'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <div className='w-full h-full bg-slate-500 flex p-3 gap-2'>
        <div className='w-50 h-full flex flex-col gap-3 bg-background rounded-xl p-3'>
          <DarkModeToggle />
          <Button variant="outline">
            Screen time
          </Button>
          <Button variant="outline">
            Kindle reading
          </Button>

        </div>
        <div className='min-h-full flex-1 bg-background rounded-xl overflow-x-hidden p-3'>

          <div className='p-2 outline rounded-xl overflow-scroll'>
            <HeatmapVisual data={[{
              "app": "com.google.Chrome",
              "device_id": "Unknown",
              "device_model": "Unknown",
              "usage": 15,
              "timezone": 0,
              "created_at": "2026-11-02T15:03:27.295523",
              "start_time": "2026-11-02T15:03:12",
              "end_time": "2026-11-02T15:03:27"
            },]} />
          </div>
        </div>
      </div>

    </>
  )
}

export default App
