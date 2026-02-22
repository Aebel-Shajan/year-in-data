import { BrowserWindow, dialog, ipcMain } from "electron";
import { etlScreentime } from "./etl/screentime.js";
import { etlChatGptMessages } from "./etl/chatGptMessages.js";
import { type Database as DatabaseType } from "better-sqlite3";
import { ConfigType, EtlLogEntry, EtlResult, EtlRun, IpcAPI } from "./sharedTypes.js";
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
    "selectFile": (extensions: string[]) => selectFile(mainWindow,extensions),
    "runEtl": (tableName: string, config: ConfigType) => runEtl(mainWindow, db, tableName, config),
    "getDataByYear": (tableName: string, year: number, dateColumn: string) => getDataByYear(db, tableName, year, dateColumn),
    "getEtlRuns": () => getEtlRuns(db),
    "getEtlRunLogs": (runId: number) => getEtlRunLogs(db, runId),
    "showDialogError": (message: string) => dialog.showErrorBox("Error", message)
  }
  Object.entries(serviceFunctionMapping).forEach(([channel, listener]) => {
    ipcMain.handle(channel, (_e, ...args) => listener(...args))
  })
}

async function selectFile(mainWindow: BrowserWindow, extensions: string[]) {
  const result = await dialog.showOpenDialog(mainWindow, {
    title: "Select a file",
    properties: ["openFile", "openDirectory"],
    filters: [{ name: "files", extensions: extensions }]
  });

  if (result.canceled) return null;
  return result.filePaths[0];
}

async function runEtl(
  mainWindow: BrowserWindow,
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

  const startedAt = new Date().toISOString()
  const insertStmt = db.prepare(
    `INSERT INTO etl_runs (table_name, status, started_at, config) VALUES (?, 'running', ?, ?)`
  )
  const result = insertStmt.run(tableName, startedAt, JSON.stringify(config))
  const runId = Number(result.lastInsertRowid)

  // Set up console interception for log capture
  const logEntries: EtlLogEntry[] = []
  let pendingLogs: EtlLogEntry[] = []
  const originalLog = console.log
  const originalError = console.error
  const originalWarn = console.warn

  function createInterceptor(level: 'log' | 'error' | 'warn', original: (...args: unknown[]) => void) {
    return (...args: unknown[]) => {
      original(...args)
      const msg = args.map(a => typeof a === 'string' ? a : JSON.stringify(a)).join(' ')
      const entry: EtlLogEntry = {
        timestamp: new Date().toISOString(),
        level,
        message: msg,
        runId,
      }
      logEntries.push(entry)
      pendingLogs.push(entry)
    }
  }

  const flushInterval = setInterval(() => {
    if (pendingLogs.length > 0) {
      const batch = pendingLogs
      pendingLogs = []
      for (const entry of batch) {
        mainWindow.webContents.send('etl-log', entry)
      }
    }
  }, 100)

  console.log = createInterceptor('log', originalLog)
  console.error = createInterceptor('error', originalError)
  console.warn = createInterceptor('warn', originalWarn)

  function cleanup() {
    console.log = originalLog
    console.error = originalError
    console.warn = originalWarn
    clearInterval(flushInterval)
    // Final flush
    for (const entry of pendingLogs) {
      mainWindow.webContents.send('etl-log', entry)
    }
    pendingLogs = []
  }

  try {
    console.log(`running etl for ${tableName}`)
    const etlFunction = TABLE_ETL_MAP[tableName]
    await etlFunction(db, config)
    const finishedAt = new Date().toISOString()
    const countRow = db.prepare(`SELECT COUNT(*) as count FROM ${tableName}`).get() as { count: number } | undefined
    const recordCount = countRow?.count ?? null
    cleanup()
    db.prepare(
      `UPDATE etl_runs SET status = 'success', finished_at = ?, record_count = ?, logs = ? WHERE id = ?`
    ).run(finishedAt, recordCount, JSON.stringify(logEntries), runId)
    return {
      success: true,
      runId,
      runMetadata: {}
    }
  } catch (e) {
    const finishedAt = new Date().toISOString()
    const errorMessage = `${e}`
    cleanup()
    db.prepare(
      `UPDATE etl_runs SET status = 'error', finished_at = ?, error_message = ?, logs = ? WHERE id = ?`
    ).run(finishedAt, errorMessage, JSON.stringify(logEntries), runId)
    const message = `error running etl: ${e}`
    console.log(message)
    dialog.showErrorBox("Error", message)

    return {
      success: false,
      runId,
      runMetadata: {
        message
      },
    }
  }
}

function getEtlRuns(db: DatabaseType): EtlRun[] {
  const stmt = db.prepare(`SELECT * FROM etl_runs ORDER BY started_at DESC`)
  return stmt.all() as EtlRun[]
}

function getEtlRunLogs(db: DatabaseType, runId: number): EtlLogEntry[] {
  const row = db.prepare(`SELECT logs FROM etl_runs WHERE id = ?`).get(runId) as { logs: string | null } | undefined
  if (!row?.logs) return []
  try {
    return JSON.parse(row.logs) as EtlLogEntry[]
  } catch {
    return []
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
