import base64
import binascii
import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from app.schemas.chat import ChatAttachment, ChatMessage, ChatRequest, ChatResponse
from app.services.openrouter import OpenRouterError, OpenRouterService

router = APIRouter(prefix="/api")
SYSTEM_INSTRUCTIONS = (
    "You are a helpful, concise assistant. Answer clearly and accurately. "
    "If you are uncertain, say so instead of inventing facts."
)
MAX_ATTACHMENT_BYTES = 10_000_000
IMAGE_TYPES = {"image/png", "image/jpeg", "image/webp", "image/gif"}
TEXT_TYPES = {"text/plain", "text/markdown", "text/csv", "application/json", "application/xml", "text/xml", "text/yaml", "application/yaml"}
TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".json", ".xml", ".yaml", ".yml", ".py", ".js", ".ts", ".tsx", ".jsx", ".sql", ".html", ".css"}
MEDIA_TYPES = {"audio/mpeg", "audio/wav", "audio/mp4", "audio/x-m4a", "video/mp4", "video/webm", "video/quicktime"}


def get_openrouter_service(request: Request) -> OpenRouterService:
    return request.app.state.openrouter_service


def build_provider_messages(payload: ChatRequest) -> list[dict]:
    user_messages = [message.model_dump() for message in payload.messages if message.role != "system"]
    if not user_messages or user_messages[-1]["role"] != "user":
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="The conversation must end with a user message.")
    if not payload.attachments:
        return [{"role": "system", "content": SYSTEM_INSTRUCTIONS}, *user_messages]

    content: list[dict] = [{"type": "text", "text": user_messages[-1]["content"]}]
    notes: list[str] = []
    for attachment in payload.attachments:
        validate_attachment(attachment)
        if attachment.content_type in IMAGE_TYPES:
            content.append({"type": "image_url", "image_url": {"url": attachment.data_url}})
        elif attachment.content_type in TEXT_TYPES or any(attachment.filename.lower().endswith(ext) for ext in TEXT_EXTENSIONS):
            encoded = attachment.data_url.split(",", 1)[-1]
            try:
                extracted = base64.b64decode(encoded, validate=True).decode("utf-8", errors="replace")[:80_000]
            except (binascii.Error, UnicodeError) as exc:
                raise HTTPException(status_code=400, detail=f"Could not read {attachment.filename}.") from exc
            notes.append(f"Contents of {attachment.filename}:\n{extracted}")
        elif attachment.content_type in MEDIA_TYPES:
            notes.append(f"{attachment.filename} is attached as {attachment.content_type}. This model receives only the media metadata; do not claim to have analyzed its contents.")
        else:
            raise HTTPException(status_code=415, detail=f"Unsupported attachment type: {attachment.filename}")
    if notes:
        content[0]["text"] += "\n\n" + "\n\n".join(notes)
    user_messages[-1] = {"role": "user", "content": content}
    return [{"role": "system", "content": SYSTEM_INSTRUCTIONS}, *user_messages]


def validate_attachment(attachment: ChatAttachment) -> None:
    if attachment.size > MAX_ATTACHMENT_BYTES:
        raise HTTPException(status_code=413, detail=f"{attachment.filename} is larger than 10 MB.")
    if not attachment.data_url.startswith("data:") or ";base64," not in attachment.data_url:
        raise HTTPException(status_code=400, detail=f"Invalid upload data for {attachment.filename}.")
    encoded = attachment.data_url.split(",", 1)[1]
    try:
        raw_size = len(base64.b64decode(encoded, validate=True))
    except binascii.Error as exc:
        raise HTTPException(status_code=400, detail=f"Invalid upload data for {attachment.filename}.") from exc
    if raw_size > MAX_ATTACHMENT_BYTES or abs(raw_size - attachment.size) > max(1024, raw_size // 10):
        raise HTTPException(status_code=400, detail=f"The size of {attachment.filename} could not be verified.")


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    service: OpenRouterService = Depends(get_openrouter_service),
) -> ChatResponse:
    provider_messages = build_provider_messages(payload)
    try:
        answer = await service.create_completion(provider_messages)
    except OpenRouterError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
    return ChatResponse(message=ChatMessage(role="assistant", content=answer))


@router.post("/chat/stream")
async def chat_stream(payload: ChatRequest, service: OpenRouterService = Depends(get_openrouter_service)) -> StreamingResponse:
    provider_messages = build_provider_messages(payload)

    async def events() -> AsyncIterator[str]:
        try:
            yielded = False
            async for delta in service.stream_completion(provider_messages):
                yielded = True
                yield f"event: delta\ndata: {json.dumps({'content': delta})}\n\n"
            if not yielded:
                yield f"event: error\ndata: {json.dumps({'message': 'The AI provider returned an empty response.'})}\n\n"
            else:
                yield "event: done\ndata: {}\n\n"
        except OpenRouterError as exc:
            yield f"event: error\ndata: {json.dumps({'message': str(exc)})}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
