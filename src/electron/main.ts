import {app, BrowserWindow} from "electron"
import path from "path"
import { isDev } from "./util.js"

app.on("ready", () => {
  const mainWindow = new BrowserWindow({})
  if (isDev()) {
    mainWindow.loadURL("http://localhost:5123")
  } else {
    const bundledAppPath = path.join(app.getAppPath(), 'dist-react/index.html')
    mainWindow.loadFile(bundledAppPath)
  }
})