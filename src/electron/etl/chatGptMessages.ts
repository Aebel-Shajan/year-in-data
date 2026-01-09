


export const chatGptMessagesSql = `
CREATE TABLE IF NOT EXISTS chat_gpt_messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT
  conversation_id TEXT,
  conversation_title: TEXT,
  message_id: TEXT,
  create_time: TEXT,
  role: TEXT,
  content_type: TEXT,
  full_content: TEXT,
  UNIQUE(app, device_id, start_time)
)
`

export interface ChatGptMessagesRecord {
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


export function etlChatGptMessages() {
  
}