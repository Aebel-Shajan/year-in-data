import { useState } from 'react'
import DarkModeToggle from './components/dark-mode-toggle'
import ScreenTimeDashboard from './pages/screentime-dashboard'
import ChatGptMessageDashboard from './pages/chatgpt-message-dashboard';
import ZshHistoryCommandsDashboard from './pages/zsh-history-commands-dashboard';
import { Button } from './components/ui/button';
import type { IpcAPI } from 'src/electron/sharedTypes';
declare global {
  interface Window {
    electronAPI: IpcAPI
  }
}

function App() {

  const [selectedPage, setSelectedPage] = useState("screenTime")

  // i cba implementing hash router 
  const pageMapping: { [key: string]: React.ReactNode } = {
    "screenTime": <ScreenTimeDashboard />,
    "chatgptMessages": <ChatGptMessageDashboard />,
    "zshHistoryCommands": <ZshHistoryCommandsDashboard />
  }


  return (
    <>
      <div className='w-full h-full bg-slate-500 flex p-3 gap-2'>
        <div className='w-50 h-full flex flex-col gap-3 bg-background rounded-xl '>
          <div className='font-extrabold text-xl w-full border-b border-accent flex items-center justify-center py-5'>
            📊 year-in-data
          </div>
          <div className='flex flex-col w-full flex-1 px-2'>
            {Object.keys(pageMapping).map((pageName) => {
              return (
                <Button onClick={() => setSelectedPage(pageName)} variant={"ghost"} className='flex justify-start'>
                  {pageName}
                </Button>
              )
            })}
          </div>
          <div className='p-4'>
          <DarkModeToggle />

          </div>


        </div>
        <div className=' flex-1 bg-background rounded-xl overflow-x-hidden overflow-y-scroll w-full h-full'>
          {pageMapping[selectedPage]}
        </div>
      </div>

    </>
  )
}

export default App
