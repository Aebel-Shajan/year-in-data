import decompress from "decompress";
import { readFile } from 'node:fs/promises';
import fs from 'node:fs';
import { type Database as DatabaseType } from 'better-sqlite3';
import { ConfigType } from '../sharedTypes.js';
import path from 'node:path';


export const kindleReadingSessionsSql = `
CREATE TABLE IF NOT EXISTS kindle_reading_sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  asin TEXT,
  product_name TEXT,
  start_time TEXT,
  end_time TEXT,
  total_reading_ms INTEGER,
  datetime TEXT,
  UNIQUE(asin, start_time)
)
`

export const kindleBooksCompletedSql = `
CREATE TABLE IF NOT EXISTS kindle_books_completed (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  asin TEXT,
  product_name TEXT,
  completed_date TEXT,
  datetime TEXT,
  UNIQUE(asin, completed_date)
)
`

export interface KindleReadingSessionRecord {
  asin: string,
  product_name: string,
  start_time: string,
  end_time: string,
  total_reading_ms: number,
  datetime: string
}

export interface KindleBooksCompletedRecord {
  asin: string,
  product_name: string,
  completed_date: string,
  datetime: string
}

interface KindleConfig extends ConfigType {
  zipPath: string,
  targetDir: string
}

export async function etlKindleReadingSessions(
  db: DatabaseType,
  conf: ConfigType
) {
  const config = conf as KindleConfig
  const { sessions, booksCompleted } = await extract(config.zipPath, config.targetDir)
  const sessionRecords = transformSessions(sessions)
  const completedRecords = transformBooksCompleted(booksCompleted)
  loadSessions(db, sessionRecords)
  loadBooksCompleted(db, completedRecords)
}

function clearDirIfExists(dir: string) {
  if (fs.existsSync(dir)) {
    console.log("Cleared contents of ", dir)
    fs.rmSync(dir, { recursive: true, force: true });
  }
}

const SESSIONS_CSV_PATH = "Kindle.ReadingInsights/datasets/Kindle.reading-insights-sessions_with_adjustments/Kindle.reading-insights-sessions_with_adjustments.csv"
const BOOKS_COMPLETED_CSV_PATH = "Kindle.ReadingInsights/datasets/Kindle.UserUniqueTitlesCompleted/Kindle.UserUniqueTitlesCompleted.csv"

async function extract(
  zipPath: string,
  targetDir: string
): Promise<{ sessions: string, booksCompleted: string }> {
  clearDirIfExists(targetDir)
  await decompress(zipPath, targetDir, {
    filter: file => file.path === SESSIONS_CSV_PATH || file.path === BOOKS_COMPLETED_CSV_PATH
  });

  const sessionsPath = path.join(targetDir, SESSIONS_CSV_PATH)
  const booksCompletedPath = path.join(targetDir, BOOKS_COMPLETED_CSV_PATH)

  const sessions = await readFile(sessionsPath, 'utf-8')
  const booksCompleted = await readFile(booksCompletedPath, 'utf-8')

  console.log("Extracted kindle CSVs from zip file.")
  return { sessions, booksCompleted }
}

function transformSessions(csvContent: string): KindleReadingSessionRecord[] {
  // strip BOM if present
  const clean = csvContent.replace(/^\uFEFF/, '')
  const lines = clean.split('\n').filter(line => line.trim().length > 0)
  const header = lines[0].split(',')

  const records: KindleReadingSessionRecord[] = []
  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(',')
    const row: Record<string, string> = {}
    header.forEach((col, idx) => {
      row[col.trim()] = (values[idx] ?? '').trim()
    })
    records.push({
      asin: row['ASIN'] ?? '',
      product_name: row['product_name'] ?? '',
      start_time: row['start_time'] ?? '',
      end_time: row['end_time'] ?? '',
      total_reading_ms: parseInt(row['total_reading_milliseconds'] ?? '0', 10),
      datetime: row['start_time'] ?? ''
    })
  }

  console.log(`Transformed ${records.length} kindle reading session records.`)
  return records
}

function transformBooksCompleted(csvContent: string): KindleBooksCompletedRecord[] {
  const clean = csvContent.replace(/^\uFEFF/, '')
  const lines = clean.split('\n').filter(line => line.trim().length > 0)
  const header = lines[0].split(',')

  const records: KindleBooksCompletedRecord[] = []
  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(',')
    const row: Record<string, string> = {}
    header.forEach((col, idx) => {
      row[col.trim()] = (values[idx] ?? '').trim()
    })

    // asin_date_and_content_type is like "B002RI9KAE_2025-04-23_AUTOMATIC"
    const asinDateField = row['asin_date_and_content_type'] ?? ''
    const parts = asinDateField.split('_')
    const asin = parts[0] ?? ''
    const completedDate = parts[1] ?? ''

    records.push({
      asin,
      product_name: row['product_name'] ?? '',
      completed_date: completedDate,
      datetime: completedDate ? `${completedDate}T00:00:00Z` : ''
    })
  }

  console.log(`Transformed ${records.length} kindle books completed records.`)
  return records
}

function loadSessions(
  db: DatabaseType,
  records: KindleReadingSessionRecord[]
) {
  const insert = db.prepare(`
    INSERT OR IGNORE INTO kindle_reading_sessions
    (asin, product_name, start_time, end_time, total_reading_ms, datetime)
    VALUES
    (@asin, @product_name, @start_time, @end_time, @total_reading_ms, @datetime)
  `);

  const insertMany = db.transaction((records: KindleReadingSessionRecord[]) => {
    for (const record of records) {
      try {
        insert.run(record);
      } catch {
        console.log("error whilst trying to insert kindle session record: ", record)
      }
    }
  });

  insertMany(records);
  console.log(`Inserted ${records.length} kindle reading session records.`);
}

function loadBooksCompleted(
  db: DatabaseType,
  records: KindleBooksCompletedRecord[]
) {
  const insert = db.prepare(`
    INSERT OR IGNORE INTO kindle_books_completed
    (asin, product_name, completed_date, datetime)
    VALUES
    (@asin, @product_name, @completed_date, @datetime)
  `);

  const insertMany = db.transaction((records: KindleBooksCompletedRecord[]) => {
    for (const record of records) {
      try {
        insert.run(record);
      } catch {
        console.log("error whilst trying to insert kindle books completed record: ", record)
      }
    }
  });

  insertMany(records);
  console.log(`Inserted ${records.length} kindle books completed records.`);
}
