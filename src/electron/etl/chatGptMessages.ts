import fs from 'node:fs';
import decompress from "decompress";
import { readFile } from 'node:fs/promises';
import { type Database as DatabaseType } from 'better-sqlite3';
import { ConfigType } from '../sharedTypes.js';
import path from 'node:path';
import pl from 'nodejs-polars';



export const chatGptMessagesSql = `
CREATE TABLE IF NOT EXISTS chat_gpt_messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  conversation_id TEXT,
  conversation_title TEXT,
  message_id TEXT,
  role TEXT,
  content_type TEXT,
  full_content TEXT,
  datetime TEXT,
  UNIQUE(conversation_id, message_id)
)
`

export interface ChatGptMessagesRecord {
  conversation_id: string,
  conversation_title: string,
  message_id: string,
  // parent: string, // too complicated to process also whats the point bruh
  // children: string[],
  role: "user" | "assistant",
  content_type: string,
  full_content: string,
  datetime: string
}

export interface ChatGptMessagesRawRecord {
  conversation_id: string,
  conversation_title: string,
  message_id: string,
  // parent: string, // too complicated to process also whats the point bruh
  // children: string[],
  create_time: string,
  role: "user" | "assistant",
  content_type: string,
  full_content: string,
}

interface ChatGptConfig extends ConfigType {
  zipPath: string,
  targetDir: string
}

export async function etlChatGptMessages(
  db: DatabaseType,
  conf: ConfigType
) {
  const config = conf as ChatGptConfig
  const conversationJson = await extract(config.zipPath, config.targetDir)
  const messageRecords = await transform(conversationJson)
  load(db, messageRecords)
}

function clearDirIfExists(dir: string) {
  if (fs.existsSync(dir)) {
    // recursive: true deletes subfolders
    // force: true ignores the error if the folder doesn't exist
    console.log("Cleared contents of ", dir)
    fs.rmSync(dir, { recursive: true, force: true });
  }
}


type JsonPrimitive = string | number;
type JsonValue = JsonPrimitive | JsonObject | JsonValue[];
type JsonObject = { [key: string]: JsonValue };

;
async function extract(
  zipPath: string,
  targetDir: string
): Promise<JsonObject[]> {
  clearDirIfExists(targetDir)
  const files = await decompress(zipPath, targetDir, {
    filter: file => file.path == "conversations.json"
  });
  const jsonPath = path.join(targetDir, files[0].path)
  const rawJsonData = await readFile(jsonPath, 'utf-8');
  const conversationJson = JSON.parse(rawJsonData);
  console.log("Extracted conversation json from zip file.", conversationJson.length)
  return conversationJson as JsonObject[]
}

async function transform(
  conversationJson: JsonObject[]
): Promise<ChatGptMessagesRecord[]> {
  const flattenedData = conversationJson.map(flattenMessages).flat()
  let df = pl.DataFrame(flattenedData)

  df = df.withColumn(
    pl
      .col("create_time")
      .cast(pl.Float64)
      .mul(1000)
      .cast(pl.Datetime("ms"))
      .cast(pl.String)    
      .alias("datetime")
  )
  df = df.drop("create_time")

  return df.toRecords() as unknown as ChatGptMessagesRecord[] // genius
}



function flattenMessages(conversation: JsonObject): ChatGptMessagesRawRecord[] {
  const conversation_id = conversation.id as string
  const conversation_title = conversation.title as string
  const chatMessagesObjects = Object.values(conversation.mapping)
  const messages: ChatGptMessagesRawRecord[] = []
  chatMessagesObjects.forEach(chatMessage => {
    try {
      const flattenedMessage: ChatGptMessagesRawRecord = {
        conversation_id: conversation_id ?? "",
        conversation_title: conversation_title ?? "",
        message_id: chatMessage.id ?? "",
        // parent: chatMessage.parent ?? "",
        // children: chatMessage.children ?? [],
        create_time: chatMessage.message?.create_time ?? "",
        role: chatMessage.message?.author.role ?? "",
        content_type: chatMessage.message?.content.content_type ?? "",
        full_content: ""
      }
      if (flattenedMessage.content_type === "text") {
        const fullContentParts: string[] = chatMessage.message?.content.parts as string[] ?? []
        flattenedMessage.full_content = fullContentParts.join(" ")
      }
      messages.push(flattenedMessage)
    } catch {
      console.error("Error encountered whilst trying to process message \n", chatMessage)
    }
  })

  return messages
}

function load(
  db: DatabaseType,
  records: ChatGptMessagesRecord[]
) {
  const insert = db.prepare(`
    INSERT OR IGNORE INTO chat_gpt_messages
    (
      conversation_id,
      conversation_title,
      message_id,
      role,
      content_type,
      full_content,
      datetime
    )
    VALUES
    (
      @conversation_id,
      @conversation_title,
      @message_id,
      @role,
      @content_type,
      @full_content,
      @datetime
     )
  `);

  const insertMany = db.transaction((records: ChatGptMessagesRecord[]) => {
    for (const record of records) {
      try {
        insert.run(record);
      } catch {
        console.log("error whilst trying to log record: ", record)
      }
    }
  });

  insertMany(records);
  console.log(`Inserted ${records.length} screen time records.`);
}
