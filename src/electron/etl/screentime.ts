import fs from "fs";
import path from "path";
import os from "os";
import sqlite3, { Database } from "better-sqlite3";

export const screenTimeSql  = `
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
`
export interface ScreenTimeRecord {
  app: string;
  device_id: string;
  device_model: string;
  usage: number;
  timezone: number | null;
  created_at: string;
  start_time: string;
  end_time: string;
}

interface ScreenTimeRaw {
  app: string;
  usage: number;
  start_time: number;
  end_time: number;
  created_at: number;
  tz: number | null;
  device_id: string | null;
  device_model: string | null;
}


const knowledgeDb = path.join(
  os.homedir(),
  "Library/Application Support/Knowledge/knowledgeC.db"
);

function extractScreenTime(): ScreenTimeRaw[] {
  if (!fs.existsSync(knowledgeDb)) {
    console.error(`Could not find knowledgeC.db at ${knowledgeDb}.`);
    process.exit(1);
  }

  try {
    fs.accessSync(knowledgeDb, fs.constants.R_OK);
  } catch (err) {
    console.error(
      `The knowledgeC.db at ${knowledgeDb} is not readable.\nPlease grant full disk access to the application running the script (Terminal, iTerm, VSCode, etc.).`
    );
    process.exit(1);
  }

  const db = sqlite3(knowledgeDb, { readonly: true });

  const query = `
    SELECT
      ZOBJECT.ZVALUESTRING AS app, 
      (ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE) AS usage,
      (ZOBJECT.ZSTARTDATE + 978307200) as start_time, 
      (ZOBJECT.ZENDDATE + 978307200) as end_time,
      (ZOBJECT.ZCREATIONDATE + 978307200) as created_at, 
      ZOBJECT.ZSECONDSFROMGMT AS tz,
      ZSOURCE.ZDEVICEID AS device_id,
      ZMODEL AS device_model
    FROM
      ZOBJECT 
      LEFT JOIN ZSTRUCTUREDMETADATA ON ZOBJECT.ZSTRUCTUREDMETADATA = ZSTRUCTUREDMETADATA.Z_PK 
      LEFT JOIN ZSOURCE ON ZOBJECT.ZSOURCE = ZSOURCE.Z_PK 
      LEFT JOIN ZSYNCPEER ON ZSOURCE.ZDEVICEID = ZSYNCPEER.ZDEVICEID
    WHERE
      ZSTREAMNAME = '/app/usage'
    ORDER BY
      ZSTARTDATE DESC
  `;

  const rows: ScreenTimeRaw[] = db.prepare(query).all() as ScreenTimeRaw[];
  db.close();

  return rows;
}

function transformScreenTime(rows: ScreenTimeRaw[]): ScreenTimeRecord[] {
  return rows.map((r) => {
    const { app, usage, start_time, end_time, created_at, tz, device_id, device_model } = r;
    return {
      app,
      device_id: device_id ?? "Unknown",
      device_model: device_model ?? "Unknown",
      usage,
      timezone: tz,
      created_at: new Date(created_at * 1000).toISOString(),
      start_time: new Date(start_time * 1000).toISOString(),
      end_time: new Date(end_time * 1000).toISOString(),
    };
  });
}



function groupByMonth(records: ScreenTimeRecord[]): Record<string, ScreenTimeRecord[]> {
  const grouped: Record<string, ScreenTimeRecord[]> = {};
  for (const r of records) {
    const month = r.created_at.slice(0, 7); // YYYY-MM
    if (!grouped[month]) grouped[month] = [];
    grouped[month].push(r);
  }
  return grouped;
}


function loadScreenTimeToSqlite(db: Database, records: ScreenTimeRecord[]) {
  const insert = db.prepare(`
    INSERT OR IGNORE INTO screen_time
      (app, device_id, device_model, usage, timezone, created_at, start_time, end_time)
    VALUES
      (@app, @device_id, @device_model, @usage, @timezone, @created_at, @start_time, @end_time)
  `);

  const insertMany = db.transaction((records: ScreenTimeRecord[]) => {
    for (const record of records) insert.run(record);
  });

  insertMany(records);
  console.log(`Inserted ${records.length} screen time records.`);
}

export function etl_screentime(db: Database) {
  const rows = extractScreenTime();
  const records = transformScreenTime(rows);
  loadScreenTimeToSqlite(db, records)
  // Uncomment to upload to S3
  // await uploadToS3(grouped);
}

