import { useState } from 'react'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
    <div className='w-full h-full bg-gray-700 flex p-3 gap-2'>
      <div className='w-50 h-full flex flex-col gap-1 bg-gray-900 rounded-xl'>
        
      </div>
      <div className='min-h-full flex-1 bg-white rounded-xl'>

      </div>
    </div>

    </>
  )
}

export default App
