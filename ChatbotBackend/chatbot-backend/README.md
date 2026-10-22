# Chatbot backend

FastAPI API for the OpenRouter chatbot. The OpenRouter API key is loaded only by this process and is never sent to the browser.

## Setup

From `D:\Projects\FineTune\ChatbotBackend\chatbot-backend`:

```powershell
uv sync
Copy-Item .env.example .env
```

Edit `.env` and set `OPENROUTER_API_KEY` and `OPENROUTER_MODEL`. Create a key at https://openrouter.ai/keys and choose a currently available model from https://openrouter.ai/models; availability and pricing can change.

Run the API:

```powershell
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Endpoints:

- `GET /api/health` — safe health check
- `POST /api/chat` — accepts `{ "messages": [{ "role": "user", "content": "Hello" }] }`
- `/docs` — FastAPI interactive documentation

Run tests without a real key or paid request:

```powershell
uv run pytest
```
