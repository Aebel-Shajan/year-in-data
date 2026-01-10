// electron-db.ts
import { app } from "electron";
import path from "path";
import Database from "better-sqlite3";
import { screenTimeSql } from "./etl/screentime.js";
import { isDev } from "./util.js";
import { chatGptMessagesSql } from "./etl/chatGptMessages.js";

const dbPath = isDev()  ? "./year-in-data.db" : path.join(app.getPath("userData"), "year-in-data.db");
const db = new Database(dbPath);

const tables = [
  screenTimeSql,
  chatGptMessagesSql
]
tables.forEach(tableSql => {
  db.prepare(tableSql).run()
})

export { db };
