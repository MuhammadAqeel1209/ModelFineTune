"use client";

import { useState } from "react";
import type { ChatMessage as ChatMessageType } from "@/types/chat";

function renderContent(content: string) {
  const blocks = content.split(/```/);
  return blocks.map((block, index) => {
    if (index % 2 === 1) {
      const lines = block.split("\n");
      const language = lines[0].trim() || "code";
      const code = lines.slice(1).join("\n");
      return <CodeBlock key={index} language={language} code={code} />;
    }
    return <MarkdownText key={index} text={block} />;
  });
}

function MarkdownText({ text }: { text: string }) {
  return <div className="markdown-content">{text.split("\n").map((line, index) => {
    const trimmed = line.trim();
    if (!trimmed) return <br key={index} />;
    if (trimmed.startsWith("### ")) return <h4 key={index}>{trimmed.slice(4)}</h4>;
    if (trimmed.startsWith("## ")) return <h3 key={index}>{trimmed.slice(3)}</h3>;
    if (trimmed.startsWith("# ")) return <h2 key={index}>{trimmed.slice(2)}</h2>;
    if (/^[-*] /.test(trimmed)) return <li key={index}>{formatInline(trimmed.slice(2))}</li>;
    if (trimmed.startsWith("> ")) return <blockquote key={index}>{formatInline(trimmed.slice(2))}</blockquote>;
    return <p key={index}>{formatInline(trimmed)}</p>;
  })}</div>;
}

function formatInline(value: string) {
  const parts = value.split(/(`[^`]+`|\*\*[^*]+\*\*)/g);
  return parts.map((part, index) => {
    if (part.startsWith("`") && part.endsWith("`")) return <code key={index}>{part.slice(1, -1)}</code>;
    if (part.startsWith("**") && part.endsWith("**")) return <strong key={index}>{part.slice(2, -2)}</strong>;
    return part;
  });
}

function CodeBlock({ language, code }: { language: string; code: string }) {
  const [copied, setCopied] = useState(false);
  async function copy() { await navigator.clipboard.writeText(code); setCopied(true); window.setTimeout(() => setCopied(false), 1500); }
  return <div className="code-block"><div className="code-header"><span>{language}</span><button onClick={copy}>{copied ? "Copied" : "Copy code"}</button></div><pre><code>{code}</code></pre></div>;
}

export function RichChatMessage({ message }: { message: ChatMessageType }) {
  const isUser = message.role === "user";
  const [copied, setCopied] = useState(false);
  async function copyResponse() { await navigator.clipboard.writeText(message.content); setCopied(true); window.setTimeout(() => setCopied(false), 1500); }
  return <div className={`message-row ${isUser ? "message-row-user" : "message-row-assistant"}`}><div className={`message-bubble ${isUser ? "message-user" : "message-assistant"}`}><span className="message-label">{isUser ? "You" : "OpenRouter AI"}</span>{isUser && message.attachments?.map((attachment) => <div className="message-attachment" key={attachment.filename}>{attachment.content_type.startsWith("image/") ? <img src={attachment.data_url} alt={attachment.filename} /> : attachment.content_type.startsWith("video/") ? <video src={attachment.data_url} controls /> : attachment.content_type.startsWith("audio/") ? <audio src={attachment.data_url} controls /> : <span>{attachment.filename}</span>}</div>)}{isUser ? <p>{message.content}</p> : renderContent(message.content)}{!isUser && <button className="copy-response" onClick={copyResponse}>{copied ? "Copied" : "Copy response"}</button>}</div></div>;
}
