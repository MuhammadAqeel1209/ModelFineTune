import type { ChatMessage as ChatMessageType } from "@/types/chat";

export function ChatMessage({ message }: { message: ChatMessageType }) {
  const isUser = message.role === "user";
  return <div className={`message-row ${isUser ? "message-row-user" : "message-row-assistant"}`}><div className={`message-bubble ${isUser ? "message-user" : "message-assistant"}`}><span className="message-label">{isUser ? "You" : "Assistant"}</span><p>{message.content}</p></div></div>;
}
