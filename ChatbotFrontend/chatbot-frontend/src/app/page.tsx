"use client";
import { useRef, useState } from "react";
import { ModernChatWindow } from "./components/ModernChatWindow";
import { ThemeToggle } from "./components/ThemeToggle";
import { streamChat } from "./lib/api";
import type { ChatAttachment, ChatMessage } from "@/types/chat";

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>([]); const [loading, setLoading] = useState(false); const [error, setError] = useState<string | null>(null); const abortRef = useRef<AbortController | null>(null);
  async function handleSend(content: string, attachments: ChatAttachment[] = []) { if (loading) return; const user = { role: "user" as const, content, attachments }; const nextMessages = [...messages, user]; setMessages([...nextMessages, { role: "assistant", content: "" }]); setError(null); setLoading(true); const controller = new AbortController(); abortRef.current = controller; try { await streamChat(nextMessages, attachments, controller.signal, (delta) => setMessages((current) => { const copy = [...current]; const last = copy[copy.length - 1]; if (last?.role === "assistant") copy[copy.length - 1] = { ...last, content: last.content + delta }; return copy; })); } catch (requestError) { if (!controller.signal.aborted) { setError(requestError instanceof Error ? requestError.message : "Something went wrong. Please try again."); setMessages((current) => current.at(-1)?.role === "assistant" && !current.at(-1)?.content ? current.slice(0, -1) : current); } } finally { if (abortRef.current === controller) abortRef.current = null; setLoading(false); } }
  function stop() { abortRef.current?.abort(); setLoading(false); }
  function retry() { const lastUser = [...messages].reverse().find((message) => message.role === "user"); if (lastUser) void handleSend(lastUser.content, lastUser.attachments); }
  return <div className="page-shell"><ThemeToggle /><ModernChatWindow messages={messages} loading={loading} error={error} onSend={handleSend} onStop={stop} onRetry={retry} onNewChat={() => { stop(); setMessages([]); setError(null); }} /></div>;
}
