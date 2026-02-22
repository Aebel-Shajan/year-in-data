import { BrowserWindow, dialog, ipcMain } from "electron";
import { etlScreentime } from "./etl/screentime.js";
import { etlChatGptMessages } from "./etl/chatGptMessages.js";
import { type Database as DatabaseType } from "better-sqlite3";
import { ConfigType, EtlResult, IpcAPI } from "./sharedTypes.js";
import { etlZshHistoryCommands } from "./etl/zshHistoryCommands.js";
import { etlHsbcStatements } from "./etl/hsbcStatements.js";
import { etlKindleReadingSessions } from "./etl/kindleReadingSessions.js";



const TABLE_ETL_MAP: Record<string, (db: DatabaseType, config: ConfigType) => void | Promise<void>> = {
  "screen_time": etlScreentime,
  "chat_gpt_messages": etlChatGptMessages,
  "zsh_history_commands": etlZshHistoryCommands,
  "hsbc_transactions": etlHsbcStatements,
  "kindle_reading_sessions": etlKindleReadingSessions
}
// open to opinions on this, should i simplify this? get rid of registry pattern?
export function registerIpcHandlers(mainWindow: BrowserWindow, db: DatabaseType) {
  const serviceFunctionMapping: IpcAPI = {
    "selectFile": () => selectFile(mainWindow),
    "runEtl": (tableName: string, config: ConfigType) => runEtl(db, tableName, config),
    "getDataByYear": (tableName: string, year: number, dateColumn: string) => getDataByYear(db, tableName, year, dateColumn),
    "showDialogError": (message: string) => dialog.showErrorBox("Error", message)
  }
  Object.entries(serviceFunctionMapping).forEach(([channel, listener]) => {
    ipcMain.handle(channel, (_e, ...args) => listener(...args))
  })
}

async function selectFile(mainWindow: BrowserWindow) {
  const result = await dialog.showOpenDialog(mainWindow, {
    title: "Select a file",
    properties: ["openFile"],
    filters: [{ name: "zip files", extensions: ["zip"] }]
  });

  if (result.canceled) return null;
  return result.filePaths[0];
}

async function runEtl(
  db: DatabaseType, 
  tableName: string, 
  config: Record<string, string|number>
): Promise<EtlResult> {
  const message = `Attempting to run etl for ${tableName}`
  console.log(message)
  if (!Object.keys(TABLE_ETL_MAP).includes(tableName)) {
    const message = `Couldn't find tableName ${tableName} in sqlite db`
    console.log(message)
    return {
      success: false,
      runMetadata: {
        message: message
      },
    }
  }
  try {
    console.log(`running etl for ${tableName}`)
    const etlFunction = TABLE_ETL_MAP[tableName]
    const metadata = await etlFunction(db, config)
    return {
      success: true,
      runMetadata: metadata ?? {}
    }
  } catch (e) {
    const message = `error running etl: ${e}`
    console.log(message)
    dialog.showErrorBox("Error", message)

    return {
      success: false,
      runMetadata: {
        message
      },
    }
  }
}

async function getDataByYear(
  db: DatabaseType,
  tableName: string,
  year: number,
  dateColumn: string
): Promise<Record<string, string | number>[]> {
  console.log(`Getting ${tableName} data from db`)
  //  TEMPORARY FOR DEV
  // TODO: ADD SOME SAFETY TO THIS
  console.log(tableName, year, dateColumn)
  const stmt = db.prepare(`
    SELECT * FROM ${tableName}
    WHERE strftime('%Y', ${dateColumn}) = '${year}'
    ORDER BY ${dateColumn} DESC
  `,);
  const records: Record<string, string | number>[] = stmt.all() as Record<string, string | number>[];
  console.log(`Retrieved ${records.length} records.`)
  return records;
}
