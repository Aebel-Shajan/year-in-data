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

const dbPath = isDev()  ? "./year-in-data.db" : path.join(app.getPath("userData"), "year-in-data.db");
const db = new Database(dbPath);

const tables = [
  screenTimeSql,
  chatGptMessagesSql,
  zshHistoryCommandsSql,
  hsbcStatementsSql,
  kindleReadingSessionsSql,
  kindleBooksCompletedSql
]
tables.forEach(tableSql => {
  try {
    db.prepare(tableSql).run()
  } catch(e) {
    console.error("Failed to build sqlite table: ", tableSql)
    throw e
  }
})

export { db };
