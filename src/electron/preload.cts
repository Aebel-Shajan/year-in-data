import { contextBridge, ipcRenderer } from "electron";

contextBridge.exposeInMainWorld('electronAPI', {
  extractScreenTime: () => ipcRenderer.invoke("etl-screen-time"),
  getScreenTimeByYear: (year: number) =>  ipcRenderer.invoke("get-screen-time-by-year", year)
})
