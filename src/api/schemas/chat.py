"""Pydantic schemas for chat."""

from typing import Optional
from pydantic import BaseModel


class SessionCreate(BaseModel):
    access_token: str
    title: str = "New Diagram"


class SessionResponse(BaseModel):
    session_id: str


class MessageSend(BaseModel):
    access_token: str
    session_id: str
    text: str
    model_id: int = 7
    ratio: str = "16:9"


class MessageResponse(BaseModel):
    message_id: str


class StatusResponse(BaseModel):
    status: int
    image_model: Optional[str] = None
    image_ratio: Optional[str] = None
    file_url: list[str] = []


class ExpandRequest(BaseModel):
    access_token: str
    message: str


class ExpandResponse(BaseModel):
    expanded: str
