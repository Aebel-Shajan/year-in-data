// electron-db.ts
import { app } from "electron";
import path from "path";
import Database from "better-sqlite3";
import { screenTimeSql } from "./etl/screentime.js";
import { isDev } from "./util.js";
import { chatGptMessagesSql } from "./etl/chatGptMessages.js";
import { zshHistoryCommandsSql } from "./etl/zshHistoryCommands.js";
import { hsbcStatementsSql } from "./etl/hsbcStatements.js";
import { kindleReadingSessionsSql, kindleBooksCompletedSql } from "./etl/kindleReadingSessions.js";

export const etlRunsSql = `CREATE TABLE IF NOT EXISTS etl_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  table_name TEXT NOT NULL,
  status TEXT NOT NULL,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  record_count INTEGER,
  error_message TEXT,
  config TEXT,
  logs TEXT
)`;

const dbPath = isDev()  ? "./year-in-data.db" : path.join(app.getPath("userData"), "year-in-data.db");
const db = new Database(dbPath);

const tables = [
  screenTimeSql,
  chatGptMessagesSql,
  zshHistoryCommandsSql,
  hsbcStatementsSql,
  kindleReadingSessionsSql,
  kindleBooksCompletedSql,
  etlRunsSql
]
tables.forEach(tableSql => {
  try {
    db.prepare(tableSql).run()
  } catch(e) {
    console.error("Failed to build sqlite table: ", tableSql)
    throw e
  }
})

// Migration: add logs column to existing etl_runs tables
try {
  db.prepare(`ALTER TABLE etl_runs ADD COLUMN logs TEXT`).run();
} catch {
  // Column already exists
}

export { db };
