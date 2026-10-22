"use client";

import { FormEvent, useEffect, useRef, useState } from "react";

export function ModernChatInput({ disabled, onSend }: { disabled: boolean; onSend: (content: string) => void }) {
  const [value, setValue] = useState("");
  const ref = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const textarea = ref.current;
    if (!textarea) return;
    textarea.style.height = "auto";
    textarea.style.height = `${Math.min(textarea.scrollHeight, 140)}px`;
  }, [value]);

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const content = value.trim();
    if (!content || disabled) return;
    onSend(content);
    setValue("");
  }

  return <form className="chat-input-form" onSubmit={submit}><textarea ref={ref} value={value} onChange={(event) => setValue(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); event.currentTarget.form?.requestSubmit(); } }} placeholder="Message OpenRouter AI..." rows={1} maxLength={8000} disabled={disabled} aria-label="Message" /><button className="send-button" type="submit" disabled={disabled || !value.trim()} aria-label="Send message">{disabled ? "..." : "↑"}</button></form>;
}
