from contextlib import asynccontextmanager
import sys
from pathlib import Path

# Allow `python app/main.py` to resolve the top-level `app` package.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import get_settings
from app.services.openrouter import OpenRouterService


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.openrouter_service = OpenRouterService(settings)
    yield
    await app.state.openrouter_service.close()


def create_app() -> FastAPI:
    application = FastAPI(title="OpenRouter Chatbot API", lifespan=lifespan)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    application.include_router(router)
    return application


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
