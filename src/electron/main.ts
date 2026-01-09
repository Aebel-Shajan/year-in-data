import { app, BrowserWindow } from "electron"
import path from "path"
import { getPreloadPath, isDev } from "./util.js"
import { registerIpcHandlers } from "./services.js"
import { db } from "./electron-db.js"

app.on("ready", () => {
  const mainWindow = new BrowserWindow({
    webPreferences: {
      preload: getPreloadPath()
    }
  })
  if (isDev()) {
    mainWindow.loadURL("http://localhost:5123")
  } else {
    const bundledAppPath = path.join(app.getAppPath(), 'dist-react/index.html')
    mainWindow.loadFile(bundledAppPath)
  }
  registerIpcHandlers(mainWindow, db)
})


