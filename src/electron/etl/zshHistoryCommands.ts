import path from "path";
import os from "os";
import fs from "fs";
import pl from "nodejs-polars"
import Database, { type Database as DatabaseType } from "better-sqlite3";
import { ConfigType } from "../sharedTypes.js";

export const zshHistoryCommandsSql = `
CREATE TABLE IF NOT EXISTS zsh_history_commands (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  datetime TEXT,
  command TEXT,
  count INTEGER,
  UNIQUE(datetime, command)
)
`

export interface ZshHistoryCommandsRecord {
  datetime: string,  
  command: string,
  count: number
}

interface ZshHistoryCommandsRawRecord {
  timestamp: number;   // unix seconds epoch
  command: string;
}

export function etlZshHistoryCommands(
  db: DatabaseType,
  conf: ConfigType
) {
  const rawRecords = extract()
  const records = transform(rawRecords)
  load(db, records)
}

function extract(): ZshHistoryCommandsRawRecord[] {
  const zshHistoryPath = path.join(
    os.homedir(),
    ".zsh_history"
  );
  const historyFile = fs.readFileSync(zshHistoryPath, "utf8");
  const lines = historyFile.split("\n");
  const rows = []
  for (const line of lines) {
    // format: : 1705071243:0;git status
    if (!line.startsWith(": ")) continue;

    const match = line.match(/^: (\d+):\d+;(.*)$/);
    if (!match) continue;

    rows.push({
      timestamp: Number(match[1]),
      command: match[2].split(" ")[0], // why not the full command? i don't want to mess with secrets and env vars
    });

  }
  return rows
}

function transform(records: ZshHistoryCommandsRawRecord[]): ZshHistoryCommandsRecord[] {
  let df = pl.DataFrame(records)
  df = df
    .withColumn(
      pl
        .col("timestamp")
        .cast(pl.Float64)
        .mul(1000)
        .cast(pl.Datetime("ms"))        // cast to Polars datetime
        .alias("datetime")
        .cast(pl.String)
    )
    .drop("timestamp")
    .withColumn(pl.lit(1).alias("count"))

  return df.toRecords() as unknown as ZshHistoryCommandsRecord[]
}


function load(
  db: DatabaseType,
  records: ZshHistoryCommandsRecord[]
) {
  const insert = db.prepare(`
    INSERT OR IGNORE INTO zsh_history_commands
    (
      datetime,
      command,
      count
    )
    VALUES
    (
      @datetime,
      @command,
      @count
     )
  `);

  const insertMany = db.transaction((records: ZshHistoryCommandsRecord[]) => {
    for (const record of records) {
      try {
        insert.run(record);
      } catch (e) {
        console.log("error whilst trying to log record: ", record)
        console.log(e)
      }
    }
  });

  insertMany(records);
  console.log(`Inserted ${records.length} screen time records.`);
}