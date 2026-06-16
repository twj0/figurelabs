"""Chat and session routes."""

import asyncio
from typing import Callable
from fastapi import FastAPI, HTTPException

from ..schemas.chat import (
    SessionCreate,
    SessionResponse,
    MessageSend,
    MessageResponse,
    StatusResponse,
    ExpandRequest,
    ExpandResponse,
)


def register_chat_routes(
    app: FastAPI,
    create_session: Callable,
    send_message: Callable,
    get_status: Callable,
    expand_prompt: Callable,
):
    """Register chat and session routes."""

    @app.post("/api/session", response_model=SessionResponse)
    async def api_create_session(body: SessionCreate):
        sid = await create_session(body.access_token, body.title)
        if not sid:
            raise HTTPException(status_code=400, detail="Failed to create session")
        return SessionResponse(session_id=sid)

    @app.post("/api/message", response_model=MessageResponse)
    async def api_send_message(body: MessageSend):
        mid = await send_message(
            body.access_token,
            body.session_id,
            body.text,
            body.model_id,
            body.ratio,
        )
        if not mid:
            raise HTTPException(status_code=400, detail="Failed to send message")
        return MessageResponse(message_id=mid)

    @app.get("/api/status/{message_id}", response_model=StatusResponse)
    async def api_get_status(message_id: str, token: str):
        st = await get_status(token, message_id)
        if st is None:
            raise HTTPException(status_code=404, detail="Message not found")
        return StatusResponse(
            status=st.get("status", 0),
            image_model=st.get("imageModel"),
            image_ratio=st.get("imageRatio"),
            file_url=st.get("fileUrl") or [],
        )

    @app.post("/api/expand", response_model=ExpandResponse)
    async def api_expand(body: ExpandRequest):
        expanded = await expand_prompt(body.access_token, body.message)
        if expanded is None:
            raise HTTPException(status_code=502, detail="Prompt expansion failed")
        return ExpandResponse(expanded=expanded)
