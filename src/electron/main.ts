import { app, BrowserWindow, ipcMain } from "electron"
import path from "path"
import { getPreloadPath, isDev } from "./util.js"
import { etl_screentime, ScreenTimeRecord } from "./etl/screentime.js"
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


  ipcMain.handle("etl-screen-time", (_event) => {
    console.log("extracting screen time")
    try {
      etl_screentime(db)
    } catch (exc) {
      console.log("Error whilst extracting screen time", exc)
    }
    return { success: true };
  });

  // IPC handler to fetch records for a specific year
  ipcMain.handle("get-screen-time-by-year", (_event, year: number) => {
    console.log("Getting screen time from db")
    const stmt = db.prepare(`
    SELECT * FROM screen_time
    WHERE strftime('%Y', start_time) = ?
    ORDER BY start_time DESC
  `);
    const records: ScreenTimeRecord[] = stmt.all(year.toString()) as ScreenTimeRecord[];
    return records;
  });
})


