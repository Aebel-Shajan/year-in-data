import { dirname } from "node:path";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import pl from "nodejs-polars"

export async function readJson<T>(
  filePath: string
): Promise<T> {
  const raw = await readFile(filePath, "utf-8");
  return JSON.parse(raw) as T;
}

export async function saveJson<T>(
  filePath: string,
  data: T,
  pretty = true
): Promise<void> {
  await mkdir(dirname(filePath), { recursive: true });

  const json = JSON.stringify(
    data,
    null,
    pretty ? 2 : undefined
  );

  await writeFile(filePath, json, "utf-8");
}

type Seen = WeakSet<object>;

export function inferType(value: unknown, seen: Seen): string {
  if (value === null) return "null";
  if (Array.isArray(value)) {
    if (value.length === 0) return "unknown[]";
    return `${inferType(value[0], seen)}[]`;
  }

  const t = typeof value;

  if (t !== "object") return t;

  if (seen.has(value as object)) return "unknown";
  seen.add(value as object);

  const entries = Object.entries(value as Record<string, unknown>)
    .map(([key, val]) => `  ${key}: ${inferType(val, seen)};`)
    .join("\n");

  return `{\n${entries}\n}`;
}

export function toTsInterface(
  name: string,
  obj: unknown
): string {
  const body = inferType(obj, new WeakSet());
  return `interface ${name} ${body}`;
}



export function displayTable(df: pl.DataFrame, limit:number = 10) {
  console.log(df.shape)
  console.table(df.head(limit).toRecords());
}


export function maskColumn(df: pl.DataFrame, column: string) {
 return df.withColumn(pl.col(column).str.slice(0, 3).str.padEnd(6, "*"))
}