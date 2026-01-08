import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { useState } from "react";


export default function ChatGptMessageDashboard() {
  const [filePath, setFilePath] = useState<string | null>(null)

  function clearSelectedFilePath() {
    setFilePath(null)
  }

  async function selectZipFile() {
    const path = await window.electronAPI.selectFile()
    if (!path) return
    setFilePath(path)
  }


  return (
    <div className=' w-full h-fit p-3 flex flex-col gap-3'>

      <div className='p-3 outline rounded-xl flex items-center justify-between sticky top-3 bg-background'>
        <div className='font-extrabold text-2xl'>
          ChatGpt messages
        </div>

        <div className='flex'>
          <Dialog>
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
  
              <Button className="w-fit">
                Extract chatgpt message data
              </Button>
              }


            </DialogContent>
          </Dialog>

        </div>

      </div>
    </div>
  )
}