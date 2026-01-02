// electron-db.ts
import { app } from "electron";
import path from "path";
import Database from "better-sqlite3";

const dbPath = path.join(app.getPath("userData"), "my-app.db");
const db = new Database(dbPath);

// Unique constraint prevents inserting the same app record for same device + start time
db.prepare(`
  CREATE TABLE IF NOT EXISTS screen_time (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app TEXT NOT NULL,
    device_id TEXT,
    device_model TEXT,
    usage REAL,
    timezone INTEGER,
    created_at TEXT,
    start_time TEXT,
    end_time TEXT,
    UNIQUE(app, device_id, start_time)
  )
`).run();

export { db };
