import type { ChatAttachment, ChatMessage } from "@/types/chat";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function streamChat(messages: ChatMessage[], attachments: ChatAttachment[], signal: AbortSignal, onDelta: (content: string) => void): Promise<void> {
  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl.replace(/\/$/, "")}/api/chat/stream`, { method: "POST", headers: { "Content-Type": "application/json", Accept: "text/event-stream" }, body: JSON.stringify({ messages: messages.map(({ attachments: _attachments, ...message }) => message), attachments }), signal });
  } catch {
    if (signal.aborted) return;
    throw new Error("Could not connect to the chatbot server. Is the backend running?");
  }
  if (!response.ok) { const data = (await response.json().catch(() => null)) as { detail?: string } | null; throw new Error(data?.detail || "The chatbot request failed."); }
  if (!response.body) throw new Error("The chatbot returned no stream.");
  const reader = response.body.getReader(); const decoder = new TextDecoder(); let buffer = "";
  while (true) { const { value, done } = await reader.read(); if (done) break; buffer += decoder.decode(value, { stream: true }); const events = buffer.split("\n\n"); buffer = events.pop() ?? ""; for (const event of events) { const type = event.match(/^event: (.+)$/m)?.[1]; const raw = event.match(/^data: (.+)$/m)?.[1]; if (!raw) continue; const data = JSON.parse(raw) as { content?: string; message?: string }; if (type === "delta" && data.content) onDelta(data.content); if (type === "error") throw new Error(data.message || "The chatbot stream failed."); } }
}
