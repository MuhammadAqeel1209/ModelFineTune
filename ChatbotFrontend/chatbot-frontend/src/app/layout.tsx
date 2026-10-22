import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = { title: "OpenRouter Chatbot", description: "A simple AI chatbot powered by OpenRouter" };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en"><body>{children}</body></html>; }
