"use client";
import { useRef } from "react";
import type { ChatMessage as ChatMessageType } from "@/types/chat";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";

export function ChatWindow({ messages, loading, error, onSend, onNewChat }: { messages: ChatMessageType[]; loading: boolean; error: string | null; onSend: (content: string) => void; onNewChat: () => void }) {
  const endRef = useRef<HTMLDivElement>(null);
  return <main className="chat-card"><div className="chat-toolbar"><div><p className="eyebrow">CONVERSATION</p><h1>OpenRouter Chatbot</h1></div><button className="new-chat-button" onClick={onNewChat} disabled={loading}>New chat</button></div><div className="messages" aria-live="polite">{messages.length === 0 && <div className="empty-state"><div className="spark">✦</div><h2>How can I help?</h2><p>Ask a question to start a conversation.</p></div>}{messages.map((message, index) => <ChatMessage key={`${message.role}-${index}`} message={message} />)}{loading && <div className="typing"><span /><span /><span /> Assistant is thinking...</div>}<div ref={endRef} /></div>{error && <div className="error-box" role="alert">{error}</div>}<ChatInput disabled={loading} onSend={onSend} /><p className="hint">Enter to send · Shift + Enter for a new line</p></main>;
}
