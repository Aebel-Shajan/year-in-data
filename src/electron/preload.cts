import { contextBridge, ipcRenderer } from "electron";
import type { IpcRendererAPI, EtlLogEntry } from "./sharedTypes";

let etlLogHandler: ((_event: unknown, entry: EtlLogEntry) => void) | null = null;

// could be more concise but this is more readable ig + we have type ch
const api: IpcRendererAPI = {
  runEtl: (...args) => ipcRenderer.invoke("runEtl", ...args),
  getDataByYear: (...args)  => ipcRenderer.invoke("getDataByYear", ...args),
  getEtlRuns: () => ipcRenderer.invoke("getEtlRuns"),
  getEtlRunLogs: (runId) => ipcRenderer.invoke("getEtlRunLogs", runId),
  selectFile: (...args) => ipcRenderer.invoke("selectFile", ...args),
  showDialogError: (...args) => ipcRenderer.invoke("showDialogError", ...args),
  onEtlLog: (callback: (entry: EtlLogEntry) => void) => {
    if (etlLogHandler) {
      ipcRenderer.removeListener('etl-log', etlLogHandler);
    }
    etlLogHandler = (_event: unknown, entry: EtlLogEntry) => callback(entry);
    ipcRenderer.on('etl-log', etlLogHandler);
  },
  removeEtlLogListener: () => {
    if (etlLogHandler) {
      ipcRenderer.removeListener('etl-log', etlLogHandler);
      etlLogHandler = null;
    }
  }
}

contextBridge.exposeInMainWorld('electronAPI', api)
