export type MessageRole = "user" | "assistant";
export type ChatAttachment = { filename: string; content_type: string; size: number; data_url: string };
export type ChatMessage = { role: MessageRole; content: string; attachments?: ChatAttachment[] };
