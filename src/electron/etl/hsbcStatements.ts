import fs from "fs";
import path from "path";
import { type Database as DatabaseType } from "better-sqlite3";
import { ConfigType } from "../sharedTypes.js";
import { getDocument } from "pdfjs-dist/legacy/build/pdf.mjs";

export const hsbcStatementsSql = `
CREATE TABLE IF NOT EXISTS hsbc_transactions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TEXT,
  type TEXT,
  details TEXT,
  amount REAL,
  statement_date TEXT,
  datetime TEXT,
  UNIQUE(date, type, details, amount, statement_date)
)
`;

export interface HsbcTransactionRecord {
  date: string;
  type: string;
  details: string;
  amount: number;
  statement_date: string;
  datetime: string;
}

interface BankTransaction {
  date: string;
  type: string;
  details: string;
  amount: number;
}

interface PdfTextRecord {
  text: string;
  x: number;
  y: number;
  width: number;
  height: number;
  page: number;
}

interface HsbcStatementsConfig extends ConfigType {
  statementsDir: string;
}

export async function etlHsbcStatements(
  db: DatabaseType,
  conf: ConfigType
) {
  const config = conf as HsbcStatementsConfig;

  const files = fs.readdirSync(config.statementsDir)
    .filter(f => f.endsWith(".pdf"))
    .sort();

  console.log(`Found ${files.length} PDF statements in ${config.statementsDir}`);

  const allRecords: HsbcTransactionRecord[] = [];

  for (const pdfFile of files) {
    const filePath = path.join(config.statementsDir, pdfFile);
    const statementDate = pdfFile.replace("_Statement.pdf", "").replace(".pdf", "");

    const rawRecords = await extract(filePath);
    const bankTransactions = transform(rawRecords);

    // Add statement_date and datetime to each record
    const records = bankTransactions.map(tx => {
      const datetime = convertToDatetime(tx.date, statementDate);
      return {
        ...tx,
        statement_date: statementDate,
        datetime
      };
    });

    allRecords.push(...records);
    console.log(`${pdfFile}: ${records.length} transactions`);
  }

  console.log(`Total extracted: ${allRecords.length} transactions`);
  load(db, allRecords);
}

function convertToDatetime(date: string, statementDate: string): string {
  // date format: "18 Dec 24", statementDate: "2025-01-16"
  const monthMap: Record<string, string> = {
    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
    "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
    "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
  };

  const parts = date.split(" ");
  if (parts.length !== 3) return statementDate;

  const day = parts[0].padStart(2, "0");
  const month = monthMap[parts[1]] || "01";
  const year = "20" + parts[2];

  return `${year}-${month}-${day}`;
}

async function extract(pdfPath: string): Promise<PdfTextRecord[]> {
  const dataBuffer = fs.readFileSync(pdfPath);
  const pdfData = new Uint8Array(dataBuffer);
  const pdfDoc = await getDocument({ data: pdfData }).promise;
  const textRecords: PdfTextRecord[] = [];

  for (let i = 1; i < pdfDoc.numPages; i++) {
    const page = await pdfDoc.getPage(i);
    const textContent = await page.getTextContent();

    for (const item of textContent.items) {
      const unTypedItem = item as Record<string, unknown>;
      const transform = unTypedItem.transform as number[];
      const y = Math.round(transform[5]);
      const x = Math.round(transform[4]);
      const textRecord: PdfTextRecord = {
        text: unTypedItem.str as string,
        x: x,
        y: y,
        width: unTypedItem.width as number,
        height: unTypedItem.height as number,
        page: i
      };

      textRecords.push(textRecord);
    }
  }
  return textRecords;
}

function isNumberString(str: string): boolean {
  if (str.replace(",", "").trim() === "") return false;
  return Number.isFinite(Number(str.replace(",", "")));
}

function isRecordDate(record: PdfTextRecord): boolean {
  const text = record.text;
  const xAlign = 53;
  if (text.split(" ").length !== 3) return false;
  const [day, , year] = text.split(" ");
  if (!isNumberString(day) || !isNumberString(year)) return false;
  if (Math.abs(record.x - xAlign) > 2) return false;
  return true;
}

function isRecordType(record: PdfTextRecord): boolean {
  const xAlign = 113;
  if (record.text.length > 3) return false;
  if (Math.abs(record.x - xAlign) > 2) return false;
  return true;
}

function isRecordDetail(record: PdfTextRecord): boolean {
  const xAlign = 140;
  if (record.text.replace(" ", "").length === 0) return false;
  if (Math.abs(record.x - xAlign) > 2) return false;
  return true;
}

function isRecordPaidOut(record: PdfTextRecord): boolean {
  const xRight = record.x + record.width;
  const xRightAlign = 390;
  if (!isNumberString(record.text)) return false;
  if (Math.abs(xRight - xRightAlign) > 4) return false;
  return true;
}

function isRecordPaidIn(record: PdfTextRecord): boolean {
  const xRight = record.x + record.width;
  const xRightAlign = 470;
  if (!isNumberString(record.text)) return false;
  if (Math.abs(xRight - xRightAlign) > 2) return false;
  return true;
}

function transform(textRecords: PdfTextRecord[]): BankTransaction[] {
  const sortedRecords = textRecords.sort((recordA, recordB) => {
    const lowerPage = recordA.page < recordB.page;
    const lowerY = recordA.y < recordB.y;
    return Number(lowerPage) + Number(lowerY);
  });

  const bankTransactions: BankTransaction[] = [];
  const emptyRecord: BankTransaction = {
    date: "",
    type: "",
    details: "",
    amount: 0
  };
  const currentRecord: BankTransaction = { ...emptyRecord };

  type SearchStates = "DATE_OR_TYPE" | "DETAIL_OR_AMOUNT";
  let searchingFor: SearchStates = "DATE_OR_TYPE";

  sortedRecords.forEach((record: PdfTextRecord) => {
    if ((searchingFor === "DATE_OR_TYPE") && isRecordDate(record)) {
      currentRecord.date = record.text;
      searchingFor = "DATE_OR_TYPE";
      return;
    }
    if (searchingFor === "DATE_OR_TYPE" && isRecordType(record)) {
      currentRecord.type = record.text;
      searchingFor = "DETAIL_OR_AMOUNT";
      return;
    }
    if (searchingFor === "DETAIL_OR_AMOUNT" && isRecordDetail(record)) {
      currentRecord.details += " " + record.text;
      searchingFor = "DETAIL_OR_AMOUNT";
      return;
    }

    if (searchingFor === "DETAIL_OR_AMOUNT") {
      if (isRecordPaidOut(record)) {
        currentRecord.amount = -1 * Number(record.text.replace(",", ""));
        bankTransactions.push({ ...currentRecord });
        currentRecord.details = "";
        searchingFor = "DATE_OR_TYPE";
        return;
      }

      if (isRecordPaidIn(record)) {
        currentRecord.amount = Number(record.text.replace(",", ""));
        bankTransactions.push({ ...currentRecord });
        currentRecord.details = "";
        searchingFor = "DATE_OR_TYPE";
        return;
      }
    }
  });

  return bankTransactions;
}

function load(
  db: DatabaseType,
  records: HsbcTransactionRecord[]
) {
  const insert = db.prepare(`
    INSERT OR IGNORE INTO hsbc_transactions
    (
      date,
      type,
      details,
      amount,
      statement_date,
      datetime
    )
    VALUES
    (
      @date,
      @type,
      @details,
      @amount,
      @statement_date,
      @datetime
    )
  `);

  const insertMany = db.transaction((records: HsbcTransactionRecord[]) => {
    for (const record of records) {
      try {
        insert.run(record);
      } catch (e) {
        console.log("error whilst trying to insert record: ", record);
        console.log(e);
      }
    }
  });

  insertMany(records);
  console.log(`Inserted ${records.length} HSBC transaction records.`);
}

// Run as standalone script: npx tsx src/electron/etl/hsbcStatements.ts <statementsDir>
// Or after transpile: node dist-electron/etl/hsbcStatements.js <statementsDir>
if (import.meta.url === `file://${process.argv[1]}`) {
  const statementsDir = process.argv[2] || "./notebooks/data/hsbcStatements";
  const dbPath = process.argv[3] || "./year-in-data.db";

  console.log(`Running standalone ETL`);
  console.log(`  Statements dir: ${statementsDir}`);
  console.log(`  Database: ${dbPath}`);

  import("better-sqlite3").then(async ({ default: Database }) => {
    const db = new Database(dbPath);
    db.prepare(hsbcStatementsSql).run();

    await etlHsbcStatements(db, { statementsDir });

    db.close();
    console.log("Done.");
  });
}
