import { useState } from 'react'
import DarkModeToggle from './components/dark-mode-toggle'
import ScreenTimeDashboard from './pages/screentime-dashboard'
import ChatGptMessageDashboard from './pages/chatgpt-message-dashboard';
import ZshHistoryCommandsDashboard from './pages/zsh-history-commands-dashboard';
import { Button } from './components/ui/button';
import type { IpcRendererAPI } from 'src/electron/sharedTypes';
import HsbcTransactionsDashboard from './pages/hsbc-transactions-dashboard';
import KindleReadingDashboard from './pages/kindle-reading-dashboard';
import EtlRunsDashboard from './pages/etl-runs-dashboard';
import { YearSelect } from './components/year-select';


declare global {
  interface Window {
    electronAPI: IpcRendererAPI
  }
}

function App() {

  const [selectedPage, setSelectedPage] = useState("screenTime")
  const [selectedYear, setSelectedYear] = useState(2025)

  // i cba implementing hash router 
  const pageMapping: { [key: string]: React.ReactNode } = {
    "screenTime": <ScreenTimeDashboard selectedYear={selectedYear} />,
    "chatgptMessages": <ChatGptMessageDashboard selectedYear={selectedYear} />,
    "zshHistoryCommands": <ZshHistoryCommandsDashboard selectedYear={selectedYear} />,
    "hsbcTransactions": <HsbcTransactionsDashboard selectedYear={selectedYear} />,
    "kindleReading": <KindleReadingDashboard selectedYear={selectedYear} />,
    "etlRuns": <EtlRunsDashboard />
  }


  return (
    <>
      <div className='w-full h-full bg-slate-500 flex p-3 gap-2'>
        <div className='w-70 h-full flex flex-col gap-3 bg-background rounded-xl '>
          <div className=' w-full border-b border-accent flex items-center justify-between  p-5 gap-1'>
            <div className='font-extrabold text-xl'>

            📊 year-in-data
            </div>
          <YearSelect value={selectedYear} onChange={(value) => setSelectedYear(value)} />
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
