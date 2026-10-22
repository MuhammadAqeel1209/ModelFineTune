"use client";
import { FormEvent, useState } from "react";

export function ChatInput({ disabled, onSend }: { disabled: boolean; onSend: (content: string) => void }) {
  const [value, setValue] = useState("");
  function submit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); const content = value.trim(); if (!content || disabled) return; onSend(content); setValue(""); }
  return <form className="chat-input-form" onSubmit={submit}><textarea value={value} onChange={(event) => setValue(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); event.currentTarget.form?.requestSubmit(); } }} placeholder="Ask anything..." rows={1} maxLength={8000} disabled={disabled} aria-label="Message" /><button type="submit" disabled={disabled || !value.trim()}>{disabled ? "Sending..." : "Send"}</button></form>;
}
