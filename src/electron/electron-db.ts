// electron-db.ts
import { app } from "electron";
import path from "path";
import Database from "better-sqlite3";
import { screenTimeSql } from "./etl/screentime.js";

const dbPath = path.join(app.getPath("userData"), "my-app.db");
const db = new Database(dbPath);

// Unique constraint prevents inserting the same app record for same device + start time
const tables = [
  screenTimeSql
]
tables.forEach(tableSql => {
  db.prepare(tableSql).run()
})

export { db };
