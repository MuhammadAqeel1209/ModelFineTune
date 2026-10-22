from typing import Literal

from pydantic import BaseModel, Field, field_validator


MessageRole = Literal["system", "user", "assistant"]


class ChatMessage(BaseModel):
    role: MessageRole
    content: str = Field(min_length=1, max_length=8_000)

    @field_validator("content")
    @classmethod
    def content_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Message content must not be blank")
        return value


class ChatAttachment(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    content_type: str = Field(min_length=1, max_length=120)
    size: int = Field(ge=1, le=10_000_000)
    data_url: str = Field(min_length=20, max_length=14_000_000)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=30)
    attachments: list[ChatAttachment] = Field(default_factory=list, max_length=5)


class ChatResponse(BaseModel):
    message: ChatMessage
