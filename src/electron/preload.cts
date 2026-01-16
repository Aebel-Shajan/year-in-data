import { contextBridge, ipcRenderer } from "electron";
import { IpcAPI } from "./sharedTypes";

// could be more concise but this is more readable ig + we have type ch
const api: IpcAPI = {
  runEtl: (...args) => ipcRenderer.invoke("runEtl", ...args),
  getDataByYear: (...args)  => ipcRenderer.invoke("getDataByYear", ...args),
  selectFile: (...args) => ipcRenderer.invoke("selectFile", ...args),
  showDialogError: (...args) => ipcRenderer.invoke("showDialogError", ...args)
}

contextBridge.exposeInMainWorld('electronAPI', api)
