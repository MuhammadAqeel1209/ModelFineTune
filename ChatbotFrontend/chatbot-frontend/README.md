# Chatbot frontend

This Next.js App Router frontend provides the chat UI. It sends conversation history to the FastAPI backend; it never receives or uses the OpenRouter key.

## Setup

From `D:\Projects\FineTune\ChatbotFrontend\chatbot-frontend`:

```powershell
Copy-Item .env.local.example .env.local
npm install
npm run dev
```

Open http://localhost:3000. Set `NEXT_PUBLIC_API_BASE_URL` in `.env.local` if the backend uses another URL. Build with `npm run build`.
