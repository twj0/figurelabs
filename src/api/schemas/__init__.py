"""Schemas package."""

from .accounts import (
    AccountOut,
    RegisterRequest,
    RegisterResponse,
    DuckMailVerifyRequest,
    LabelUpdate,
)
from .chat import (
    SessionCreate,
    SessionResponse,
    MessageSend,
    MessageResponse,
    StatusResponse,
    ExpandRequest,
    ExpandResponse,
)
from .stats import StatsResponse, TotalCountsResponse

__all__ = [
    "AccountOut",
    "RegisterRequest",
    "RegisterResponse",
    "DuckMailVerifyRequest",
    "LabelUpdate",
    "SessionCreate",
    "SessionResponse",
    "MessageSend",
    "MessageResponse",
    "StatusResponse",
    "ExpandRequest",
    "ExpandResponse",
    "StatsResponse",
    "TotalCountsResponse",
]
