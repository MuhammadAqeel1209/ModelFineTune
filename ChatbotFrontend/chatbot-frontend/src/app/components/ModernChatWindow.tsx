"use client";

import type { ChatAttachment, ChatMessage as ChatMessageType } from "@/types/chat";
import { RichChatMessage } from "./RichChatMessage";
import { EnhancedChatInput } from "./EnhancedChatInput";

const suggestions = [
  ["💡", "Explain a complex topic"],
  ["💻", "Help me write some code"],
  ["✍️", "Improve my writing"],
  ["🚀", "Brainstorm new ideas"],
];

export function ModernChatWindow({ messages, loading, error, onSend, onStop, onNewChat, onRetry }: { messages: ChatMessageType[]; loading: boolean; error: string | null; onSend: (content: string, attachments?: ChatAttachment[]) => void; onStop: () => void; onNewChat: () => void; onRetry: () => void }) {
  const empty = messages.length === 0;
  return <main className="chat-card"><header className="chat-toolbar"><div className="brand-lockup"><div className="brand-mark">✦</div><div><h1>OpenRouter AI</h1><p><span className="status-dot" /> AI Assistant</p></div></div><button className="new-chat-button" onClick={onNewChat} disabled={loading}><span>＋</span> New chat</button></header><div className={`messages ${empty ? "messages-empty" : ""}`} aria-live="polite">{empty ? <div className="empty-state"><div className="spark">✦</div><h2>What can I help you with?</h2><p>Ask anything. Explore ideas. Get things done.</p><div className="suggestion-grid">{suggestions.map(([icon, text]) => <button key={text} className="suggestion-card" onClick={() => onSend(text)}><span>{icon}</span>{text}<b>→</b></button>)}</div></div> : <>{messages.map((message, index) => <RichChatMessage key={`${message.role}-${index}`} message={message} />)}{loading && <div className="typing"><span /><span /><span /> <em>Generating…</em></div>}</>}</div>{error && <div className="error-box" role="alert"><span>!</span><div>{error}<button onClick={onRetry}>Try again</button></div></div>}<EnhancedChatInput disabled={loading} onSend={onSend} onStop={onStop} /><p className="hint">Enter to send <span>•</span> Shift + Enter for a new line · Drop files to attach</p></main>;
}
