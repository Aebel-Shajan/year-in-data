import { useState } from 'react'
import { Button } from './components/ui/button'
import DarkModeToggle from './components/dark-mode-toggle'

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
      <div className='min-h-full flex-1 bg-background rounded-xl'>

      </div>
    </div>

    </>
  )
}

export default App
